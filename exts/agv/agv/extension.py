import omni.ext
import omni.ui as ui
import os
import omni.kit.commands
from pxr import Gf, UsdGeom
import omni.graph.core as og

# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print(f"[omni.hello.world] some_public_function was called with {x}")
    return x ** x

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class ExtensionDataPathManager:
    def __init__(self):
        manager = omni.kit.app.get_app().get_extension_manager()
        self.extension_data_path = os.path.join(manager.get_extension_path_by_module("agv"), "data")

    def get_extension_data_path(self):
        return self.extension_data_path

class StageManager:
    def __init__(self):
        self.context = None
        self.stage = None
    
    def setup(self):
        self.context = omni.usd.get_context()
        self.stage = self.context.get_stage()
        UsdGeom.SetStageMetersPerUnit(self.stage, 0.01)

    def get_stage(self):
        if self.stage is None:
            self.setup()
        return self.stage

    def get_context(self):
        if self.context is None:
            self.setup()
        return self.context

class ActionGraphManager:
    def __init__(self, data_path_manager):
        self._data_path_manager = data_path_manager

    def create_action_graph(self):
        graph_path = f"/control_center_graph"
        keys = og.Controller.Keys
        (graph_handle, list_of_nodes, _, _) = og.Controller.edit(
            {"graph_path": graph_path, "evaluator_name": "execution"},
            {
                keys.CREATE_NODES: [
                    ("on_playback_tick", "omni.graph.action.OnPlaybackTick"),
                    ("script_node", "omni.graph.scriptnode.ScriptNode"),
                ],
                keys.SET_VALUES: [
                    ("script_node.inputs:usePath", True),
                    ("script_node.inputs:scriptPath", os.path.join(self._data_path_manager.get_extension_data_path(), "control_center.py")),
                ],
                keys.CONNECT: [
                    ("on_playback_tick.outputs:tick", "script_node.inputs:execIn"),
                ]
            }
        )

class SceneElementsManager:
    def __init__(self, stage_manager, data_path_manager):
        self._stage_manager = stage_manager
        self._data_path_manager = data_path_manager

    def create_ground_plane(self):
        omni.kit.commands.execute('CreatePayload',
                                  usd_context=self._stage_manager.get_context(),
                                  path_to='/World/GroundPlane',
                                  asset_path=os.path.join(self._data_path_manager.get_extension_data_path(), 'GroundPlane.usd'),
                                  )

    def create_payload(self):
        omni.kit.commands.execute('CreatePayload',
                                  usd_context=self._stage_manager.get_context(),
                                  path_to='/World/cast_AGV31',
                                  asset_path=os.path.join(self._data_path_manager.get_extension_data_path(), 'cast_AGV31.usdz'),
                                  )
class MyExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        print("[omni.hello.world] MyExtension startup")
        self._data_path_manager = ExtensionDataPathManager()
        self._stage_manager = StageManager()
        self._action_graph_manager = ActionGraphManager(self._data_path_manager)
        self._scene_elements_manager = SceneElementsManager(self._stage_manager, self._data_path_manager)

        self._window = ui.Window("My Window", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                def on_click():
                    self._scene_elements_manager.create_ground_plane()
                    self._scene_elements_manager.create_payload()
                    self._action_graph_manager.create_action_graph()

                with ui.HStack():
                    ui.Button("Init", clicked_fn=on_click)

    def on_shutdown(self):
        print("[omni.hello.world] MyExtension shutdown")
