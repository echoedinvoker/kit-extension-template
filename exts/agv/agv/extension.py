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

class MyExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        print("[omni.hello.world] MyExtension startup")
        self._data_path_manager = ExtensionDataPathManager()
        stage = omni.usd.get_context().get_stage()
        UsdGeom.SetStageMetersPerUnit(stage, 0.01)

        self._window = ui.Window("My Window", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                # label = ui.Label("")

                def on_click():
                    omni.kit.commands.execute('AddGroundPlaneCommand',
                                            stage=stage,
                                            planePath='/GroundPlane',
                                            axis='Z',
                                            size=2500.0,
                                            position=Gf.Vec3f(0.0, 0.0, 0.0),
                                            color=Gf.Vec3f(0.5, 0.5, 0.5)
                                              )
                    omni.kit.commands.execute('CreatePayload',
                                            usd_context=omni.usd.get_context(),
                                            path_to='/World/cast_AGV31',
                                            asset_path=os.path.join(self._data_path_manager.get_extension_data_path(), 'cast_AGV31.usdz'),
                                              )



                with ui.HStack():
                    ui.Button("Init", clicked_fn=on_click)

    def on_shutdown(self):
        print("[omni.hello.world] MyExtension shutdown")
