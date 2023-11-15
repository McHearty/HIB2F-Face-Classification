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

    def execute(self, context):
        selected_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
        
        if not selected_objects:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}

        total_face_counts = [0, 0, 0, 0]  # isosceles, equilateral, right, scalene

        for obj in selected_objects:
            bpy.ops.object.mode_set(mode='OBJECT')
            bm = bmesh.new()
            bm.from_mesh(obj.data)

            # Counters for each object
            face_counts = [0, 0, 0, 0]

            for face in bm.faces:
                if len(face.verts) == 3:
                    # Process only triangular faces
                    self.classify_triangle(face, face_counts)

            bm.free()

            # Accumulate counts
            for i in range(len(total_face_counts)):
                total_face_counts[i] += face_counts[i]

        # Update the statistics
        context.scene.face_classification_stats = total_face_counts
        return {'FINISHED'}

    def classify_triangle(self, face, face_counts):
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
        if any(angle == 90 for angle in [alpha, beta, gamma]):
            face_counts[2] += 1  # Right

        # Classify based on side lengths
        side_lengths = [a, b, c]
        unique_lengths = len(set(side_lengths))

        if unique_lengths == 1:
            face_counts[1] += 1  # Equilateral
        elif unique_lengths == 2:
            face_counts[0] += 1  # Isosceles
        else:
            face_counts[3] += 1  # Scalene

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