from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from PIL import Image
import time


app = Ursina()
window.borderless = False
window.exit_button.visible = False

class SelectedBlock():
    def __init__(self):
        self.blockType = 0
    def set(self, newBlockType):
        self.blockType = newBlockType
    def get(self):
        return self.blockType
    
selectedBlock = SelectedBlock()

tilesheet = Image.open("tilesheet.png")
iconsheet = Image.open("iconsheet.png")
def get_tile(index=0):
    imtex = tilesheet.copy().crop((12*index, 0, 12+(12*index), 12))
    imtex.save(str(index)+".png")
    texture = load_texture(str(index)+".png")
    os.remove(str(index)+".png")
    return texture
tiles = []
for t in range(12):
    tiles.append(get_tile(t))

def get_icon(index=0):
    imtex = iconsheet.copy().crop((16*index, 0, 16+(16*index), 16))
    imtex.save(str(index)+"i.png")
    texture = load_texture(str(index)+"i.png")
    os.remove(str(index)+"i.png")
    return texture
icons = []
for i in range(10):
    icons.append(get_icon(i))

voxels = []

def get_texture(offset, blockType):
    if blockType == 0 and offset[1]==1:
        return tiles[0]
    elif blockType == 0 and offset[1]==-1:
        return tiles[2]
    elif blockType == 7:
        if abs(offset[1]) == 1:
            return tiles[9]
        else:
            return tiles[8]
    elif blockType >= 8:
        return tiles[blockType+2]
    else:
        return tiles[blockType+1]

class HotbarSlot(Button):
    def __init__(self, blockType, offset=0, position=Vec2(0,0), parent=Entity, scale=1):
        super().__init__()
        self.color = color.white
        self.texture = icons[blockType]
        self.blockType = blockType
        self.parent = parent
        self.position = Vec2((offset * scale) + position.x, position.y)
        self.scale = Vec2(scale, scale)
    def on_click(self):
        selectedBlock.set(self.blockType)
    def input(self, key):
        if key == str(1 + self.blockType):
            selectedBlock.set(self.blockType)
        if key == str(0) and self.blockType == 9:
            selectedBlock.set(self.blockType)

class Hotbar(Entity):
    def __init__(self, position=Vec2(0,0), scale=1):
        super().__init__()
        self.always_on_top = True
        self.parent = camera.ui_camera
        self.position = Vec2(0, 0)
        for i in range(10):
            HotbarSlot(blockType=i, offset=i*1.1, position=position, parent=self, scale=scale)

class Face(Button):
    def __init__(self, offset, rotation, position, blockType, _color=color.white, parent=Entity):
        super().__init__(parent=parent,
            rotation=rotation,
            position=Vec3(position) + Vec3(offset[0], offset[1], offset[2]),
            model='quad',
            color=_color,
            texture=get_texture(offset=offset, blockType=blockType),
        )
        self.clicked = False
        self.clickTime = 0
        self.offset = Vec3(offset[0], offset[1], offset[2])
        self.blockType = blockType
        self.scale = Vec3(2, 2, 0.1)

    def input(self, key):
        if mouse.hovered_entity == self:
            if mouse.middle:
                selectedBlock.set(self.blockType)
            if key == Keys.left_mouse_down:
                self.clickTime = time.time()
            if key == Keys.left_mouse_up and not mouse.moving:
                t = time.time()
                if t - self.clickTime < 0.2:
                    Voxel(position=self.parent.position + self.offset, blockType=selectedBlock.get())
                elif t - self.clickTime >= 0.4:
                    self.clicked = True

class Voxel(Entity):
    def __init__(self, position=(0,0,0), blockType=0, color=color.white):
        super().__init__(parent=scene,
            position = position,
            collider = 'box'
        )
        voxels.append(self)
        self.faces = [Face(offset=[0, 1, 0], rotation=(90, 0, 0), position=position, blockType=blockType, _color=color, parent=self),
                      Face(offset=[0, 0, 1], rotation=(0, 180, 0), position=position, blockType=blockType, _color=color, parent=self),
                      Face(offset=[0, 0, -1], rotation=(0, 0, 0), position=position, blockType=blockType, _color=color, parent=self),
                      Face(offset=[1, 0, 0], rotation=(0, -90, 0), position=position, blockType=blockType, _color=color, parent=self),
                      Face(offset=[-1, 0, 0], rotation=(0, 90, 0), position=position, blockType=blockType, _color=color, parent=self),
                      Face(offset=[0, -1, 0], rotation=(-90, 0, 0), position=position, blockType=blockType, _color=color, parent=self)]
    
    def update(self):
        for f in self.faces:
            if f == mouse.hovered_entity:
               f.color = color.light_gray
            else:
                f.color = color.white
            if f.clicked:
                destroy(self)

for y in range(-2, 1):
    for z in range(12):
        for x in range(12):
            voxel = Voxel(position=(x,y,z), blockType=abs(y))

vel = Vec3(0,0,0)
direction = Vec3(0,0,0)

def update():
    if held_keys[Keys.escape]:
        application.quit()

    if mouse.left:
        camera.world_rotation_y += mouse.velocity[0] * 60
        camera.world_rotation_x -= mouse.velocity[1] * 60
        camera.world_rotation_x = clamp(camera.rotation.x, -90, 90)

    direction = Vec3(
            camera.forward * (held_keys['w'] - held_keys['s'])
            + camera.right * (held_keys['d'] - held_keys['a'])
            + camera.up * (held_keys[Keys.up_arrow] -  held_keys[Keys.down_arrow])
            ).normalized()
    camera.world_position += direction * 10 * time.dt


hotbar = Hotbar(Vec2(-10, -8.75), 2)
camera = camera

app.run()