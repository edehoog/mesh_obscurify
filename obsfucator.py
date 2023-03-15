bl_info = {
    "name": "STL Obsfucator",
    "author": "Elija de Hoog",
    "version": (0, 1),
    "blender": (3, 4, 1),
    "location": "View3d > Tool",
    "warning": "",
    "wiki_url": "",
    "category": "Edit Mesh",
}

import bpy
from bpy.types import (Panel, Operator)
from bpy_extras.io_utils import (ImportHelper, ExportHelper)
from math import radians
import json

# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

PROPS = [
    ('x_twist_angle', bpy.props.FloatProperty(name="Twist")),
    ('y_twist_angle', bpy.props.FloatProperty(name="Bend")),
    ('z_twist_angle', bpy.props.FloatProperty(name="Stretch")),
]


# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------


class SetupPanel(Panel):
    bl_label = "Setup"
    bl_idname = "PT_SetupPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Obsfucator"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row = layout.row()
        row.operator(Obscurify_OT_CleanScene.bl_idname)
        row = layout.row()
        row.operator(Obscurify_OT_ImportSTL.bl_idname)
        row = layout.row()
        row.operator(Obscurify_OT_ImportKey.bl_idname)


class DeformPanel(Panel):
    bl_label = "Deform"
    bl_idname = "PT_DeformPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Obsfucator"

    def draw(self, context):
        layout = self.layout

        col = self.layout.column()
        for (prop_name, _) in PROPS:
            row = col.row()
            row.prop(context.scene, prop_name)
        row = layout.row()
        row.operator(Obscurify_OT_Reset.bl_idname)
        row = layout.row()
        row.operator(Obscurify_OT_Deform.bl_idname)
        row = layout.row()
        row.operator(Obscurify_OT_Reform.bl_idname)


class ExportPanel(Panel):
    bl_label = "Export"
    bl_idname = "PT_ExportPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Obsfucator"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        layout.operator("export_mesh.stl", text="Export STL")
        row = layout.row()
        row.operator(Obscurify_OT_ExportKey.bl_idname)


# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class Obscurify_OT_CleanScene(Operator):
    bl_idname = "obscurify.clean_scene"
    bl_label = "Clean Scene"

    def execute(self, context):
        for obj in bpy.data.objects:
            bpy.data.objects.remove(obj)
        return {'FINISHED'}


class Obscurify_OT_ImportSTL(Operator, ImportHelper):
    bl_idname = "obscurify.import_stl"
    bl_label = "Import STL"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".stl"
    filter_glob: bpy.props.StringProperty(
        default="*.stl",
        options={'HIDDEN'})

    def execute(self, context):
        if self.filepath:
            bpy.ops.import_mesh.stl(filepath=self.filepath)

            # https://blender.stackexchange.com/questions/193622/to-control-the-bind-of-the-surface-deform-modifier-with-python

            bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
            bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
            bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
            bpy.context.object.modifiers["SimpleDeform"].deform_axis = 'X'
            bpy.context.object.modifiers["SimpleDeform"].angle = radians(0)
            bpy.context.object.modifiers["SimpleDeform"].deform_method = 'TWIST'
            bpy.context.object.modifiers["SimpleDeform.001"].deform_axis = 'X'
            bpy.context.object.modifiers["SimpleDeform.001"].angle = radians(0)
            bpy.context.object.modifiers["SimpleDeform.001"].deform_method = 'BEND'
            bpy.context.object.modifiers["SimpleDeform.002"].deform_axis = 'X'
            bpy.context.object.modifiers["SimpleDeform.002"].angle = radians(0)
            bpy.context.object.modifiers["SimpleDeform.002"].deform_method = 'STRETCH'

            mat = bpy.data.materials.new(name="STLMaterial")
            context.object.data.materials.append(mat)

        #            bpy.ops.object.mode_set(mode="EDIT")
        #            bpy.ops.mesh.subdivide(number_cuts=25)
        #            bpy.ops.object.mode_set(mode="OBJECT")

        return {'FINISHED'}


class Obscurify_OT_ImportKey(Operator, ImportHelper):
    bl_idname = "obscurify.import_key"
    bl_label = "Import Key"

    filename_ext = ".json"

    def execute(self, context):
        if self.filepath:
            with open('sample.json', 'r') as openfile:
                data = json.load(openfile)

            context.scene.x_twist_angle = float(data["parameter_1"])
            context.scene.y_twist_angle = float(data["parameter_2"])
            context.scene.z_twist_angle = float(data["parameter_3"])

            openfile.close()

        return {'FINISHED'}


class Obscurify_OT_ExportKey(Operator, ExportHelper):
    bl_idname = "obscurify.export_key"
    bl_label = "Export Key"

    filename_ext = ".json"

    def execute(self, context):
        print("Obscurify_OT_ExportKey")

        key = {
            "parameter_1": context.scene.x_twist_angle,
            "parameter_2": context.scene.y_twist_angle,
            "parameter_3": context.scene.z_twist_angle,
        }

        data = json.dumps(key)

        with open("sample.json", "w") as outfile:
            json.dump(key, outfile)

        return {'FINISHED'}


class Obscurify_OT_Deform(Operator):
    bl_idname = "obscurify.deform"
    bl_label = "Deform"

    def execute(self, context):
        bpy.context.object.modifiers["SimpleDeform"].angle = radians(context.scene.x_twist_angle)
        bpy.context.object.modifiers["SimpleDeform.001"].angle = radians(context.scene.y_twist_angle)
        bpy.context.object.modifiers["SimpleDeform.002"].angle = context.scene.z_twist_angle
        return {'FINISHED'}


class Obscurify_OT_Reform(Operator):
    bl_idname = "obscurify.reform"
    bl_label = "Reform"

    def execute(self, context):
        bpy.context.object.modifiers["SimpleDeform"].angle = -1 * radians(context.scene.x_twist_angle)
        bpy.context.object.modifiers["SimpleDeform.001"].angle = -1 * radians(context.scene.y_twist_angle)
        bpy.context.object.modifiers["SimpleDeform.002"].angle = -1 * context.scene.z_twist_angle
        return {'FINISHED'}


class Obscurify_OT_Reset(Operator):
    bl_idname = "obscurify.reset"
    bl_label = "Reset"

    def execute(self, context):
        bpy.context.object.modifiers["SimpleDeform"].angle = radians(0)
        bpy.context.object.modifiers["SimpleDeform.001"].angle = radians(0)
        bpy.context.object.modifiers["SimpleDeform.002"].angle = 0

        context.scene.x_twist_angle = 0
        context.scene.y_twist_angle = 0
        context.scene.z_twist_angle = 0
        return {'FINISHED'}


# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (SetupPanel, DeformPanel, ExportPanel, Obscurify_OT_Reset, Obscurify_OT_Reform, Obscurify_OT_CleanScene,
           Obscurify_OT_Deform, Obscurify_OT_ImportKey, Obscurify_OT_ImportSTL, Obscurify_OT_ExportKey)


def register():
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
