import bpy
import bmesh
import math
from bpy.props import IntVectorProperty

bl_info = {
    "name": "Face Classification",
    "author": "Calculating Contriverman",
    "version": (1, 0, 0),
    "blender": (3, 3, 1),
    "category": "Halo Infinite",
    "location": "View3D > Sidebar",
    "description": "This version of the script will classify the faces of all selected mesh objects when the operator is executed. The total counts across all selected objects are accumulated and displayed in the panel.",
}

class OT_FaceClassificationOperator(bpy.types.Operator):
    bl_idname = "object.face_classification_operator"
    bl_label = "Classify Selected Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        self.isosceles_count = 0
        self.equilateral_count = 0
        self.right_count = 0
        self.scalene_count = 0

    def execute(self, context):
        mesh_objects_found = False
        for obj in bpy.context.selected_objects:
            mesh_objects_found = True
            bpy.ops.object.mode_set(mode='OBJECT')
            bm = bmesh.new()
            bm.from_mesh(obj.data)

            self.classify_triangles(bm.faces)

            bm.free()

        if mesh_objects_found:
            # Update the statistics
            context.scene.face_classification_stats = [self.isosceles_count,
                                                       self.equilateral_count,
                                                       self.right_count,
                                                       self.scalene_count]
            status = {'FINISHED'}

        else:
            self.report({'ERROR'}, "No mesh objects selected")
            status = {'CANCELLED'}

        return status


    def classify_triangles(self, bm_faces):
        for face in bm_faces:
            if len(face.verts) == 3:
                vertices = [v.co for v in face.verts]

                # Calculate the lengths of the sides
                a = (vertices[1] - vertices[0]).length
                b = (vertices[2] - vertices[1]).length
                c = (vertices[0] - vertices[2]).length

                # Calculate the angles using the Law of Cosines
                alpha = math.degrees(math.acos((b**2 + c**2 - a**2) / (2 * b * c)))
                beta = math.degrees(math.acos((c**2 + a**2 - b**2) / (2 * c * a)))
                gamma = math.degrees(math.acos((a**2 + b**2 - c**2) / (2 * a * b)))

                # Classify based on angles
                if 90 in [alpha, beta, gamma]:
                    self.right_count += 1  # Right
                    ### incr. count of right and possibly scalene / isosceles intended?
                    ### if not add break here for a simple fix ###

                # Classify based on side lengths
                side_lengths = [a, b, c]
                unique_lengths = len(set(side_lengths))

                if unique_lengths == 1:
                    self.equilateral_count += 1  # Equilateral
                elif unique_lengths == 2:
                    self.isosceles_count += 1  # Isosceles
                else:
                    self.scalene_count += 1  # Scalene


class VIEW3D_PT_FaceClassificationMenu(bpy.types.Panel):
    bl_label = "Face Classification"
    bl_idname = "VIEW3D_PT_face_classification_menu"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mesh to Forge Objects'

    def draw(self, context):
        layout = self.layout
        stats = context.scene.face_classification_stats

        layout.operator("object.face_classification_operator")

        if stats:
            face_types = ["Isosceles", "Equilateral", "Right", "Scalene"]
            for i, face_type in enumerate(face_types):
                # Using "CHECKMARK" icon
                icon_type = 'CHECKMARK' if face_type in ["Isosceles", "Equilateral", "Right"] else 'ERROR'
                layout.label(text=f"{face_type}: {stats[i]}", icon=icon_type)

            # Calculate and display the Estimated Print
            estimated_print = sum(stats[:-1]) + (stats[-1] * 2)
            layout.label(text=f"Estimated Print: {estimated_print}", icon='FILE_IMAGE')

def register():
    bpy.utils.register_class(OT_FaceClassificationOperator)
    bpy.utils.register_class(VIEW3D_PT_FaceClassificationMenu)
    bpy.types.Scene.face_classification_stats = IntVectorProperty(
        name="Face Classification Stats",
        description="Statistics of face classification",
        size=4
    )

def unregister():
    bpy.utils.unregister_class(OT_FaceClassificationOperator)
    bpy.utils.unregister_class(VIEW3D_PT_FaceClassificationMenu)
    del bpy.types.Scene.face_classification_stats

if __name__ == "__main__":
    register()