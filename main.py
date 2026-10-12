from __future__ import annotations

import random
from enum import Enum, auto
from typing import Optional

from panda3d.core import loadPrcFileData
loadPrcFileData("", "fullscreen #f")
loadPrcFileData("", "win-size 1280 720")

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectFrame
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    CardMaker,
    CollisionRay,
    DirectionalLight,
    Fog,
    LineSegs,
    LPoint3f,
    LVector3f,
    NodePath,
    Plane,
    Point3,
    TextNode,
    Texture,
    TextureStage,
    Vec3,
)

from ai_learning import AITrainer
from battle_system import BattleSystem
from camera_controller import CameraController
from units import (
    AIArmy,
    PlayerArmy,
    Soldier,
    Tank,
    random_position_in_range,
    TerrainType,
    SceneryObstacle
)


class GamePhase(Enum):
    BUY_AND_DEPLOY_PLAYER = auto()
    DEPLOY_AI = auto()
    BATTLE = auto()
    RESULT = auto()


class GameManager(ShowBase):
    """Top-level game class handling phases, input, UI, and integration."""

    def __init__(self) -> None:
        ShowBase.__init__(self)

        # Use manual camera control.
        self.disableMouse()

        # Battlefield extents and deployment zones.
        self.map_half_size = 500.0
        self.player_x_min = -480.0
        self.player_x_max = -40.0
        self.ai_x_min = 40.0
        self.ai_x_max = 480.0
        self.y_min = -480.0
        self.y_max = 480.0

        # Economy 
        self.starting_points = 50000
        self.points_remaining = self.starting_points

        # Armies and systems.
        self.player_army = PlayerArmy()
        self.ai_army = AIArmy()
        self.battle_system = BattleSystem(self.player_army, self.ai_army, max_battle_time=300.0)
        self.ai_trainer = AITrainer()

        self.current_phase: GamePhase = GamePhase.BUY_AND_DEPLOY_PLAYER
        self.current_terrain: TerrainType = TerrainType.FOREST
        self.battle_timer: float = 0.0

        # For AI learning.
        self._ai_round_state = None
        self._ai_round_action: Optional[str] = None

        # Environment NodePaths
        self.ground: Optional[NodePath] = None
        self.scenery_parent: Optional[NodePath] = None
        
        # Scene setup
        self._setup_camera()
        self._setup_lighting()
        self._build_environment()

        # Drag selection state for mass spawning
        self._dragging: bool = False
        self._drag_start_pos: Optional[Point3] = None
        self._current_spawn_type: str = "soldier"
        self._drag_rect_np: Optional[NodePath] = None

        # Camera controller (RTS style).
        self.camera_controller = CameraController(self)

        # Input bindings for unit placement and phase changes.
        self._setup_controls()

        # UI
        self._setup_ui()

        # Schedule main loop.
        self.taskMgr.add(self._update_task, "update-task")

    def _setup_camera(self) -> None:
        self.camera.setPos(0, -120, 70)
        self.camera.lookAt(0, 0, 0)
        self.camLens.setFar(3000) 

    def _setup_lighting(self) -> None:
        self.render.setShaderAuto()
        
        ambient = AmbientLight("ambient")
        ambient.setColor((0.8, 0.8, 0.8, 1))
        ambient_np = self.render.attachNewNode(ambient)
        self.render.setLight(ambient_np)

        sun = DirectionalLight("sun")
        sun.setColor((0.9, 0.9, 0.9, 1)) 
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(-45, -60, 0)
        self.render.setLight(sun_np)
        
        myFog = Fog("Scene Fog")
        myFog.setColor(0.6, 0.7, 0.9)
        myFog.setLinearRange(100, 2000) 
        self.render.setFog(myFog)
        self.setBackgroundColor(0.6, 0.7, 0.9)

    def _build_environment(self) -> None:
        """Create a textured ground and scenery based on the selected terrain biome."""
        
        # 1. Clear old environment if any
        if self.ground:
            self.ground.removeNode()
        if self.scenery_parent:
            self.scenery_parent.removeNode()
            self.battle_system.scenery_grid.clear()
            
        self.scenery_parent = self.render.attachNewNode("scenery")
        
        # 2. Build Terrain Mesh
        cm = CardMaker("ground")
        ground_size = 1100.0 
        cm.setFrame(-ground_size/2, ground_size/2, -ground_size/2, ground_size/2)
        self.ground = self.render.attachNewNode(cm.generate())
        self.ground.setP(-90)
        self.ground.setPos(0, 0, 0)
        
        # 3. Setup Lighting/Fog colors based on terrain
        myFog = self.render.getFog()
        if myFog:
            if self.current_terrain == TerrainType.SNOW:
                myFog.setColor(0.8, 0.85, 0.9)
                self.setBackgroundColor(0.8, 0.85, 0.9)
            elif self.current_terrain == TerrainType.DESERT:
                myFog.setColor(0.9, 0.8, 0.6)
                self.setBackgroundColor(0.9, 0.8, 0.6)
            else:
                myFog.setColor(0.6, 0.7, 0.9)
                self.setBackgroundColor(0.6, 0.7, 0.9)

        # 4. Apply Textures based on Biome
        try:
            if self.current_terrain == TerrainType.SNOW:
                tex_path = "models/snow_terrain.png"
            elif self.current_terrain == TerrainType.DESERT:
                tex_path = "models/pure_sand_terrain.png"
            else:
                tex_path = "models/uniform_grass.png"
                
            tex_grass = self.loader.loadTexture(tex_path)
            tex_grass.setWrapU(Texture.WM_repeat)
            tex_grass.setWrapV(Texture.WM_repeat)
            tex_grass.setAnisotropicDegree(16)
            
            ts_grass = TextureStage("grass_layer")
            self.ground.setTexture(ts_grass, tex_grass)
            
            # Set tiling density
            if self.current_terrain in (TerrainType.SNOW, TerrainType.DESERT):
                grass_repeat = ground_size * 0.08  
            else:
                grass_repeat = ground_size * 0.8   
                
            self.ground.setTexScale(ts_grass, grass_repeat, grass_repeat)
            self.ground.setTexRotate(ts_grass, 13)
            
            # Base color tints
            if self.current_terrain == TerrainType.PLAINS:
                self.ground.setColorScale(1.0, 1.25, 1.0, 1.0) 
            else:
                self.ground.setColorScale(1.0, 1.0, 1.0, 1.0) 
            
            # Mud layer 
            if self.current_terrain == TerrainType.FOREST:
                tex_noise = self.loader.loadTexture("models/terrain_noise.png", "models/terrain_noise.png")
                tex_noise.setWrapU(Texture.WM_repeat)
                tex_noise.setWrapV(Texture.WM_repeat)
                
                ts_mask = TextureStage("mask_layer")
                ts_mask.setCombineRgb(TextureStage.CMReplace, TextureStage.CSPrevious, TextureStage.COSrcColor)
                ts_mask.setCombineAlpha(TextureStage.CMReplace, TextureStage.CSTexture, TextureStage.COSrcAlpha)
                self.ground.setTexture(ts_mask, tex_noise)
                self.ground.setTexScale(ts_mask, ground_size / 600.0, ground_size / 600.0)
                self.ground.setTexRotate(ts_mask, 73)
                
                tex_mud = self.loader.loadTexture("muddy_battlefield.png")
                tex_mud.setWrapU(Texture.WM_repeat)
                tex_mud.setWrapV(Texture.WM_repeat)
                tex_mud.setAnisotropicDegree(16)
                
                ts_mud = TextureStage("mud_layer")
                ts_mud.setCombineRgb(
                    TextureStage.CMInterpolate, 
                    TextureStage.CSTexture, TextureStage.COSrcColor,
                    TextureStage.CSPrevious, TextureStage.COSrcColor,
                    TextureStage.CSPrevious, TextureStage.COSrcAlpha
                )
                self.ground.setTexture(ts_mud, tex_mud)
                mud_repeat = ground_size * 0.6
                self.ground.setTexScale(ts_mud, mud_repeat, mud_repeat)
                self.ground.setTexRotate(ts_mud, 15)

        except Exception as e:
            print(f"Failed to load terrain texture: {e}")
            self.ground.setColor(0.3, 0.4, 0.2, 1) 

        # 5. Add Scenery
        try: stone_master = self.loader.loadModel("models/rock_on_ground.glb")
        except Exception: stone_master = None
            
        tree_master = NodePath("tree_master")
        try:
            trunk = self.loader.loadModel("models/box")
            trunk.reparentTo(tree_master)
            trunk.setScale(0.8, 0.8, 4.0)
            trunk.setPos(0, 0, 2.0)
            trunk.setColor(0.3, 0.15, 0.05, 1.0)
            # Lush procedural canopy
            base_z = 4.0
            import random
            
            # Determine leaf colors based on terrain
            if self.current_terrain == TerrainType.SNOW:
                c1, c2 = (0.85, 0.9, 0.95, 1.0), (0.75, 0.8, 0.9, 1.0)
            else:
                c1, c2 = (0.1, 0.35, 0.1, 1.0), (0.08, 0.28, 0.08, 1.0)
                
            for i in range(18):
                leaf = self.loader.loadModel("models/box")
                leaf.reparentTo(tree_master)
                # Random sizes for organic look
                ls = random.uniform(1.5, 2.5)
                leaf.setScale(ls, ls, ls)
                
                # Form a rough sphere
                theta = random.uniform(0, 2 * 3.14159)
                height_ratio = random.uniform(0, 1)
                r = (1.0 - height_ratio) * 2.5 + 0.5 
                
                import math
                x = math.cos(theta) * r
                y = math.sin(theta) * r
                z = base_z + (height_ratio * 5.0)
                
                leaf.setPos(x, y, z)
                leaf.setHpr(random.uniform(0,360), random.uniform(0,360), random.uniform(0,360))
                
                if random.random() > 0.5:
                    leaf.setColor(c1)
                else:
                    leaf.setColor(c2)
                
            tree_master.flattenLight()
            
            # Update HUD Text Colors for Readability
            if hasattr(self, 'status_text') and hasattr(self, 'hint_text'):
                if self.current_terrain in (TerrainType.SNOW, TerrainType.DESERT):
                    dark_color = (0.1, 0.1, 0.1, 1.0)
                    self.status_text.setFg(dark_color)
                    self.hint_text.setFg(dark_color)
                    self.phase_text.setFg((0.6, 0.2, 0.0, 1.0)) # Dark orange
                else:
                    self.status_text.setFg((0.7, 0.9, 1.0, 1.0))
                    self.hint_text.setFg((0.8, 0.8, 0.8, 1.0))
                    self.phase_text.setFg((1.0, 0.6, 0.1, 1.0))
        except Exception:
            tree_master = None

        ground_half = 500.0
        
        # Determine density based on terrain
        stone_count = 150
        tree_count = 600
        
        if self.current_terrain == TerrainType.PLAINS:
            stone_count = 20
            tree_count = 0
        elif self.current_terrain == TerrainType.DESERT:
            stone_count = 350
            tree_count = 0
        elif self.current_terrain == TerrainType.SNOW:
            stone_count = 100
            tree_count = 150
        
        if stone_master:
            for _ in range(stone_count):
                x = random.uniform(-ground_half, ground_half)
                y = random.uniform(-ground_half, ground_half)
                
                s = stone_master.copyTo(self.scenery_parent)
                s.setPos(x, y, 0)
                s.setH(random.uniform(0, 360))
                
                scale = random.uniform(1.0, 2.5) if random.random() < 0.1 else random.uniform(0.1, 0.5)
                if self.current_terrain == TerrainType.DESERT and random.random() < 0.2:
                    scale *= 2.0
                    
                s.setScale(scale)
                
                # Tint rocks in snow/desert
                if self.current_terrain == TerrainType.SNOW:
                    s.setColorScale(1.5, 1.5, 1.6, 1.0)
                elif self.current_terrain == TerrainType.DESERT:
                    s.setColorScale(1.4, 1.1, 0.8, 1.0)
                
                obs = SceneryObstacle(s.getPos(), radius=scale * 1.5)
                self.battle_system.scenery_grid.insert(obs)
        
        if tree_master and tree_count > 0:
            for _ in range(tree_count):
                x = random.uniform(-ground_half, ground_half)
                y = random.uniform(-ground_half, ground_half)
                
                t = tree_master.copyTo(self.scenery_parent)
                t.setPos(x, y, 0)
                t.setH(random.uniform(0, 360))
                scale = random.uniform(0.8, 1.6)
                t.setScale(scale)
                
                obs = SceneryObstacle(t.getPos(), radius=scale * 1.6)
                self.battle_system.scenery_grid.insert(obs)

    def _setup_controls(self) -> None:
        # Mouse clicks to place units during player deployment.
        self.accept("mouse1", self._on_left_down)
        self.accept("mouse1-up", self._on_left_up)
        
        # Toggle spawn type
        self.accept("1", self._set_spawn_type, ["soldier"])
        self.accept("2", self._set_spawn_type, ["tank"])
        
        # Toggle terrain
        self.accept("t", self._cycle_terrain)

        # Advance phase once the player is done placing.
        self.accept("enter", self._advance_phase)

        # Quit shortcut.
        self.accept("escape", self.userExit)

    def _setup_ui(self) -> None:
        try:
            ui_font = self.loader.loadFont("/c/Windows/Fonts/consola.ttf")
            ui_font.setPixelsPerUnit(100)
            ui_font.setMinfilter(Texture.FTLinearMipmapLinear)
            ui_font.setMagfilter(Texture.FTLinear)
        except Exception:
            try:
                ui_font = self.loader.loadFont("/c/Windows/Fonts/ariblk.ttf")
                ui_font.setPixelsPerUnit(100)
            except Exception:
                ui_font = None

        font_kwargs = {"font": ui_font} if ui_font else {}


        self.status_text = OnscreenText(
            text="",
            pos=(-1.28, 0.94),  
            scale=0.042,
            fg=(0.7, 0.9, 1.0, 1.0),
            shadow=(0, 0, 0, 0.5),
            shadowOffset=(0.04, 0.04),
            align=TextNode.ALeft,
            mayChange=True,
            **font_kwargs
        )
        
        self.hint_text = OnscreenText(
            text="",
            pos=(-1.28, -0.18),  
            scale=0.042,
            fg=(0.8, 0.8, 0.8, 1.0),
            shadow=(0, 0, 0, 0.5),
            shadowOffset=(0.04, 0.04),
            align=TextNode.ALeft,
            mayChange=True,
            **font_kwargs
        )

        self.phase_text = OnscreenText(
            text="",
            pos=(1.25, 0.93),
            scale=0.055,
            fg=(1.0, 0.6, 0.1, 1.0),
            shadow=(0, 0, 0, 0.8),
            shadowOffset=(0.04, 0.04),
            align=TextNode.ARight,
            mayChange=True,
            **font_kwargs
        )

        self.result_text = OnscreenText(
            text="",
            pos=(0.0, 0.0),
            scale=0.1,
            fg=(1.0, 0.8, 0.2, 1.0),
            shadow=(0, 0, 0, 1.0),
            shadowOffset=(0.05, 0.05),
            align=TextNode.ACenter,
            mayChange=True,
            **font_kwargs
        )

    def _mouse_world_position(self) -> Optional[Point3]:
        """Project the current mouse position onto the ground plane (z=0).

        Uses base.camLens.extrude() and a CollisionRay-style ray to produce
        a world-space ray, then intersects that ray with the plane.
        """

        if not self.mouseWatcherNode.hasMouse():
            return None

        mpos = self.mouseWatcherNode.getMouse()
        near_point = Point3()
        far_point = Point3()

        # Convert 2D mouse position to a 3D line in camera space.
        self.camLens.extrude(mpos, near_point, far_point)

        # Transform into world space.
        near_world = self.render.getRelativePoint(self.camera, near_point)
        far_world = self.render.getRelativePoint(self.camera, far_point)

        # Build a ray similar to CollisionRay usage.
        ray_direction = (far_world - near_world).normalized()
        ray_origin = near_world

        # Intersect ray with the ground plane z=0.
        ground_plane = Plane(Vec3(0, 0, 1), Point3(0, 0, 0))
        hit_point = Point3()
        if not ground_plane.intersectsLine(hit_point, ray_origin, ray_origin + ray_direction * 1000.0):
            return None

        return hit_point

    def _position_in_player_zone(self, pos: Point3) -> bool:
        return (
            self.player_x_min <= pos.getX() <= self.player_x_max
            and self.y_min <= pos.getY() <= self.y_max
        )

    def _set_spawn_type(self, unit_type: str) -> None:
        self._current_spawn_type = unit_type

    def _cycle_terrain(self) -> None:
        if self.current_phase != GamePhase.BUY_AND_DEPLOY_PLAYER:
            return
            
        terrains = list(TerrainType)
        idx = terrains.index(self.current_terrain)
        self.current_terrain = terrains[(idx + 1) % len(terrains)]
        
        # Clear currently placed units as terrain/obstacles changed
        for unit in self.player_army.units:
            if unit.alive:
                unit.cleanup()
        self.player_army.units.clear()
        self.points_remaining = self.starting_points
        
        self._build_environment()

    def _on_left_down(self) -> None:
        if self.current_phase != GamePhase.BUY_AND_DEPLOY_PLAYER:
            return
        
        world_pos = self._mouse_world_position()
        if world_pos is None:
            return
        
        self._dragging = True
        self._drag_start_pos = Point3(world_pos.getX(), world_pos.getY(), 0.0)
        
        # Disable camera rotation while drawing spawn box
        self.camera_controller.enable_rotation = False

    def _on_left_up(self) -> None:
        if not self._dragging:
            return
        
        self._dragging = False
        self.camera_controller.enable_rotation = True
        
        if self._drag_rect_np is not None:
            node_np = self._drag_rect_np
            assert node_np is not None
            node_np.removeNode()
            self._drag_rect_np = None
            
        end_pos = self._mouse_world_position()
        if end_pos is None or self._drag_start_pos is None:
            return
        
        assert end_pos is not None
        end_pos.setZ(0.0)
        self._spawn_formation(self._drag_start_pos, end_pos, self._current_spawn_type)

    def _update_drag_visual(self) -> None:
        if not self._dragging or self._drag_start_pos is None:
            return
        
        end_pos = self._mouse_world_position()
        if end_pos is None:
            return
        
        if self._drag_rect_np is not None:
            node_np = self._drag_rect_np
            assert node_np is not None
            node_np.removeNode()

        ls = LineSegs()
        ls.setColor(0, 1, 0, 1)
        ls.setThickness(2.0)
        
        assert self._drag_start_pos is not None
        assert end_pos is not None
        x1, y1 = self._drag_start_pos.getX(), self._drag_start_pos.getY()
        x2, y2 = end_pos.getX(), end_pos.getY()
        
        ls.drawTo(x1, y1, 5.0)
        ls.drawTo(x2, y1, 5.0)
        ls.drawTo(x2, y2, 5.0)
        ls.drawTo(x1, y2, 5.0)
        ls.drawTo(x1, y1, 5.0)
        
        node = ls.create()
        self._drag_rect_np = self.render.attachNewNode(node)

    def _spawn_formation(self, start: Point3, end: Point3, unit_type: str) -> None:
        x_min = min(start.getX(), end.getX())
        x_max = max(start.getX(), end.getX())
        y_min = min(start.getY(), end.getY())
        y_max = max(start.getY(), end.getY())
        
        # Ensure minimum size to spawn at least one
        width = max(1.0, x_max - x_min)
        height = max(1.0, y_max - y_min)
        
        if unit_type == "soldier":
            cost = Soldier.DEFAULT_STATS.cost
            spacing = 1.2
        else:
            cost = Tank.DEFAULT_STATS.cost
            spacing = 3.0
            
        cols = max(1, int(width / spacing))
        rows = max(1, int(height / spacing))
        
        # Spawn unit by unit in formation
        for r in range(rows):
            for c in range(cols):
                if self.points_remaining < cost:
                    return
                
                x = x_min + c * spacing + (spacing * 0.5)
                y = y_min + r * spacing + (spacing * 0.5)
                
                pos = Point3(x, y, 0.5)
                
                if unit_type == "soldier":
                    unit = Soldier("player", pos, self.loader, self.render)
                else:
                    unit = Tank("player", pos, self.loader, self.render)
                    
                # Small random jitter so formations aren't perfectly robotic
                pos.setX(pos.getX() + random.uniform(-0.1, 0.1))
                pos.setY(pos.getY() + random.uniform(-0.1, 0.1))
                unit.node.setPos(pos)
                
                # Face AI territory
                unit.node.setH(90)

                self.player_army.add_unit(unit)
                self.points_remaining -= cost

    def _advance_phase(self) -> None:
        if self.current_phase == GamePhase.BUY_AND_DEPLOY_PLAYER:
            self._start_ai_deployment()
        elif self.current_phase == GamePhase.RESULT:
            self._start_new_round()

    def _start_ai_deployment(self) -> None:
        """Ask the AITrainer for an army composition and spawn it."""

        player_spent = self.starting_points - self.points_remaining
        # If player placed nothing, give AI a tiny budget to prevent crashes
        ai_budget = max(10, player_spent)

        state = self.ai_trainer.build_state(self.player_army, self.ai_army, None)
        action = self.ai_trainer.select_action(state)
        # Give the AI exactly the same budget the player used, instead of the 50k max
        plan = self.ai_trainer.choose_composition(ai_budget, action)

        soldiers = plan["soldiers"]
        tanks = plan["tanks"]
        style = plan["style"]

        # Record for learning.
        self._ai_round_state = state
        self._ai_round_action = action

        # Choose spawn bands based on style.
        if style == "rush":
            x_min, x_max = self.ai_x_min, (self.ai_x_min + self.ai_x_max) * 0.5
        elif style == "defend":
            x_min, x_max = (self.ai_x_min + self.ai_x_max) * 0.5, self.ai_x_max
        else:
            x_min, x_max = self.ai_x_min, self.ai_x_max

        if style == "spread":
            y_min, y_max = self.y_min, self.y_max
        else:
            y_min, y_max = -40.0, 40.0

        for _ in range(soldiers):
            spawn_pos = random_position_in_range(x_min, x_max, y_min, y_max, z=0.5)
            unit = Soldier("ai", spawn_pos, self.loader, self.render)
            self.ai_army.add_unit(unit)

        for _ in range(tanks):
            spawn_pos = random_position_in_range(x_min, x_max, y_min, y_max, z=0.5)
            unit = Tank("ai", spawn_pos, self.loader, self.render)
            self.ai_army.add_unit(unit)

        # Any unspent points are left unused this round.
        self.current_phase = GamePhase.DEPLOY_AI

        # Immediately transition into battle.
        self._start_battle()

    def _start_battle(self) -> None:
        self.battle_timer = 0.0
        self.battle_system.start_battle()
        self.current_phase = GamePhase.BATTLE

    def _start_new_round(self) -> None:
        # Clear scene units
        for unit in self.player_army.units:
            if unit.alive:
                unit.cleanup()
        for unit in self.ai_army.units:
            if unit.alive:
                unit.cleanup()

        self.player_army.units.clear()
        self.ai_army.units.clear()

        self.points_remaining = self.starting_points
        self.current_phase = GamePhase.BUY_AND_DEPLOY_PLAYER
        self.result_text.setText("")

    def _update_task(self, task):
        from panda3d.core import ClockObject
        dt = ClockObject.getGlobalClock().getDt()

        # Camera controls are always available in every phase.
        if not self._dragging:
            self.camera_controller.enable_rotation = True
        self.camera_controller.update(dt)
        
        if self._dragging:
            self._update_drag_visual()

        if self.current_phase == GamePhase.BATTLE:
            self._update_battle(dt)

        self._update_ui()

        return task.cont

    def _update_battle(self, dt: float) -> None:
        self.battle_timer += dt
        result = self.battle_system.update(dt, self.current_terrain)

        if result in ("player", "ai", "draw"):
            self.current_phase = GamePhase.RESULT

            stats = self.battle_system.get_battle_stats()
            
            if result == "player":
                msg = "// DECISIVE VICTORY //"
                reward = -100.0
            elif result == "ai":
                msg = ">> OVERWHELMED <<"
                reward = 100.0
            else:
                msg = "-- STALEMATE --"
                reward = 0.0

            # Consider casualties in reward. 
            casualty_diff = stats.get("player_killed", 0) - stats.get("ai_killed", 0)
            reward += casualty_diff * 0.1

            # Provide the next state to the AI Trainer to finish the Q-learning episode
            next_state = self.ai_trainer.build_state(self.player_army, self.ai_army, self.battle_system)
            self.ai_trainer.finish_episode(reward, next_state)

            final_msg = f"{msg}\n\n[ PRESS ENTER FOR NEXT ROUND ]"
            if self._ai_round_action:
                final_msg += f"\n\n> AI STRATEGY PROTOCOL: '{self._ai_round_action.upper()}' <"
                
            self.result_text.setText(final_msg)

    def _update_ui(self) -> None:
        player_units = self.player_army.count()
        ai_units = self.ai_army.count()

        if self.current_phase == GamePhase.BATTLE:
            phase_label = ">>> COMBAT ENGAGED <<<"
        elif self.current_phase == GamePhase.BUY_AND_DEPLOY_PLAYER:
            phase_label = ">>> COMMANDER DEPLOYMENT MODE <<<"
        elif self.current_phase == GamePhase.DEPLOY_AI:
            phase_label = ">>> ENEMY LOGISTIC DEPLOYMENT <<<"
        else:
            phase_label = ">>> POST-ACTION REPORT <<<"

        self.phase_text.setText(phase_label)

        timer_str = f"{self.battle_timer:5.1f}s" if self.current_phase == GamePhase.BATTLE else "--"

        self.status_text.setText(
            f"TERRAIN: {self.current_terrain.name}\n"
            f"BUDGET: {self.points_remaining} pts    |    TIME: {timer_str}\n"
            f"FORCES: Player: {player_units}   ||   Enemy: {ai_units}"
        )
        
        effects_str = ""
        if self.current_terrain == TerrainType.FOREST:
            effects_str = "Tanks 30% Slower | Soldiers take 20% Less Damage"
        elif self.current_terrain == TerrainType.PLAINS:
            effects_str = "Tanks 30% Faster"
        elif self.current_terrain == TerrainType.DESERT:
            effects_str = "Soldiers 20% Slower | Tanks take 10% More Damage"
        elif self.current_terrain == TerrainType.SNOW:
            effects_str = "Tanks 40% Slower | Soldiers 10% Slower"

        self.hint_text.setText(
            f"SELECTED LOGISTIC: [{self._current_spawn_type.upper()}]\n\n"
            f"> {self.current_terrain.name} EFFECTS:\n"
            f"> {effects_str}\n\n"
            f"> System Hints:\n"
            f"> Press [T] to cycle Terrain Type\n"
            f"> Press [1] for Soldier, [2] for Tank\n"
            f"> Drag mouse in tactical zone to deploy division\n"
            f"> Press [ENTER] to execute combat phase"
        )



if __name__ == "__main__":
    game = GameManager()
    game.run()
