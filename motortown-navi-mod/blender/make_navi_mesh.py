"""Erzeugt das Navi-Modell SM_Navi und exportiert es als FBX fuer Unreal.

Aufruf (Blender 4.x):
    blender --background --python make_navi_mesh.py -- <ausgabe.fbx>
oder in Blender: Scripting-Tab -> Datei oeffnen -> Run Script (exportiert nach //SM_Navi.fbx).

Masse in cm (Unreal-Einheiten). Achsen wie in Unreal:
    +X = Blickrichtung des Displays (zum Fahrer)
    +Y = Breite, +Z = Hoehe
Der Ursprung liegt hinten an der Halterung - dort wird das Teil am Fahrzeug befestigt.

    X:  0 ---- 1.5 ------------- 3.5 -- 3.9
        [Fuss] [   Gehaeuse     ][Rahmen]
                         Display bei X = 3.55, Widget-Socket bei X = 3.6
"""

import sys

import bpy

CM = 0.01  # Blender rechnet in Metern

# Gehaeuse
BODY_W, BODY_H = 14.0, 11.0
FOOT_DEPTH, BODY_DEPTH, BEZEL_DEPTH = 1.5, 2.0, 0.4
# sichtbare Displayflaeche (muss zu config.lua ScreenWidthCm / DrawSize passen)
SCREEN_W, SCREEN_H = 12.0, 9.0
SCREEN_X = FOOT_DEPTH + BODY_DEPTH + 0.05


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for block in (bpy.data.meshes, bpy.data.materials):
        for item in list(block):
            block.remove(item)


def material(name, rgb, roughness):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def box(name, x0, x1, y0, y1, z0, z1, mat):
    """Quader zwischen den angegebenen Grenzen (cm)."""
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = ((x1 - x0) * CM, (y1 - y0) * CM, (z1 - z0) * CM)
    obj.location = ((x0 + x1) / 2 * CM, (y0 + y1) / 2 * CM, (z0 + z1) / 2 * CM)
    obj.data.materials.append(mat)
    return obj


def build():
    frame = material("M_NaviFrame", (0.02, 0.02, 0.022), 0.45)
    screen = material("M_NaviScreen", (0.0, 0.0, 0.0), 0.15)
    mount = material("M_NaviMount", (0.05, 0.05, 0.05), 0.7)

    hw, hh = BODY_W / 2, BODY_H / 2
    sw, sh = SCREEN_W / 2, SCREEN_H / 2
    x_body0, x_body1 = FOOT_DEPTH, FOOT_DEPTH + BODY_DEPTH
    x_bezel1 = x_body1 + BEZEL_DEPTH

    parts = [
        # Halterung (Saugfuss-Arm), zentriert hinter dem Gehaeuse
        box("Foot", 0.0, x_body0, -1.5, 1.5, -1.5, 1.5, mount),
        # Gehaeuse
        box("Body", x_body0, x_body1, -hw, hw, -hh, hh, frame),
        # Rahmen um das Display (4 Leisten)
        box("BezelTop", x_body1, x_bezel1, -hw, hw, sh, hh, frame),
        box("BezelBottom", x_body1, x_bezel1, -hw, hw, -hh, -sh, frame),
        box("BezelLeft", x_body1, x_bezel1, -hw, -sw, -sh, sh, frame),
        box("BezelRight", x_body1, x_bezel1, sw, hw, -sh, sh, frame),
        # Displayflaeche (liegt hinter der Minimap, sichtbar wenn das Display aus ist)
        box("Screen", x_body1, SCREEN_X, -sw, sw, -sh, sh, screen),
    ]

    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[1]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.join()
    navi = bpy.context.active_object
    navi.name = "SM_Navi"
    navi.data.name = "SM_Navi"

    # Ursprung bleibt bei (0,0,0) = Rueckseite der Halterung
    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")

    # UVs fuer Lightmaps/Materialien
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")
    return navi


def export(path):
    bpy.ops.export_scene.fbx(
        filepath=path,
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS",
        axis_forward="X",
        axis_up="Z",
        mesh_smooth_type="FACE",
        add_leaf_bones=False,
    )
    print(f"SM_Navi exportiert nach {path}")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = argv[0] if argv else bpy.path.abspath("//SM_Navi.fbx")
    clear_scene()
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 1.0
    build().select_set(True)
    export(out)


if __name__ == "__main__":
    main()
