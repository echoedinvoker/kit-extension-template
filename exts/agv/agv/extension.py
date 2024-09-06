import omni.ext
import omni.ui as ui
import os
import omni.kit.commands
from pxr import Gf, UsdGeom

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

class MyExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        print("[omni.hello.world] MyExtension startup")
        self._data_path_manager = ExtensionDataPathManager()
        self._stage_manager = StageManager()

        self._window = ui.Window("My Window", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                # label = ui.Label("")

                def on_click():
                    omni.kit.commands.execute('AddGroundPlaneCommand',
                                            stage=self._stage_manager.get_stage(),
                                            planePath='/GroundPlane',
                                            axis='Z',
                                            size=2500.0,
                                            position=Gf.Vec3f(0.0, 0.0, 0.0),
                                            color=Gf.Vec3f(0.5, 0.5, 0.5)
                                              )
                    omni.kit.commands.execute('CreatePayload',
                                            usd_context=self._stage_manager.get_context(),
                                            path_to='/World/cast_AGV31',
                                            asset_path=os.path.join(self._data_path_manager.get_extension_data_path(), 'cast_AGV31.usdz'),
                                              )



                with ui.HStack():
                    ui.Button("Init", clicked_fn=on_click)

    def on_shutdown(self):
        print("[omni.hello.world] MyExtension shutdown")
