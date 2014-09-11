import sys
import os
import re
import subprocess
import tempfile
from PIL import Image, ImageEnhance, ImageOps
import numpy as np
from splinter import Browser
import time

bro = Browser()
bro.visit('http://rupdae.superintendenciadepreciosjustos.gob.ve/usuarios/login')

import ipdb
#ipdb.set_trace()



def change_color(img):
    
    """ Cange color """        
    im = Image.open(img)
    data = np.array(im)

    #r1, g1, b1 = 255, 255, 255 
    r1, g1, b1 = 236, 0, 0 
    r2, g2, b2 = 0, 0, 0

    red, green, blue = data[:,:,0], data[:,:,1], data[:,:,2]
    mask = (red == r1) & (green == g1) & (blue == b1)
    data[:,:,:3][mask] = [r2, g2, b2]

    #ipdb.set_trace()
    im = Image.fromarray(data)
    im.save('captcha.png')
    #os.remove(img)


def change_brig(img):

    """ Change color """
    imm = Image.open(img)
    imm = imm.convert('RGBA')
    r, g, b, alpha = imm.split()
    selection = r.point(lambda i: i > 120 and 150)
    selection.save("captcha.png")
    r.paste(g, None, selection)
    imm = Image.merge("RGBA", (r, g, b, alpha))
    #imm.save("captcha.png")
    os.remove(img)

    """ Change Brightness """
    brightness = 1.0
    #peak = Image.open("captcha.png")
    enhancer = ImageEnhance.Brightness(imm)
    bright = enhancer.enhance(brightness)
    #bright.save("captcha.png")

    """ Change Contrast """
    contrast = 4.0
    enhancer = ImageEnhance.Contrast(bright)
    con = enhancer.enhance(contrast)
    con.save("captcha.png")


def crop_img(screenshot):

    #ipdb.set_trace()

    img = Image.open(screenshot)

    left = 640
    top = 376
    width = 130
    height = 40
    box = (left, top, left+width, top+height)
    area = img.crop(box)
    area.save('captcha.png','png')
    #os.remove(screenshot)




def threshold(filename, limit=100):
    img = Image.open(filename)
    m = 1.5
    img = img.resize((int(img.size[0]*m), int(img.size[1]*m))).convert('RGBA')
    pixdata = img.load()

    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            if pixdata[x, y][0] < limit:
                pixdata[x, y] = (0, 0, 0, 255)
            else:
                pixdata[x, y] = (255, 255, 255, 255)
    img.save('tmp/threshold_' + filename)
    return img.convert('L') 



def call_command(*args):
    c = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = c.communicate()
    if c.returncode != 0:
        if error:
            print error
        print "Error running `%s'" % ' '.join(args)
    return output


def tesseract(image):
    input_file = tempfile.NamedTemporaryFile(suffix='.tif')
    image.save(input_file.name)

    output_filename = input_file.name.replace('.tif', '.txt')
    call_command('tesseract', input_file.name, output_filename.replace('.txt', ''))
    
    result = open(output_filename).read()
    os.remove(output_filename)
    return clean(result)



def clean(s):
    return re.sub('[\W]', '', s)
    



def ejecutar():
    screenshot = bro.screenshot(os.getcwd()+"/")

    change_brig(screenshot)
    crop_img("captcha.png")
    img = threshold("captcha.png")
    captcha = tesseract(img)
    #time.sleep(2)
    print captcha

    bro.fill('usuario','J311968199')
    bro.fill('contrasenia','J-311968199a')
    bro.fill('captcha', str(captcha))
    bro.find_by_id('btnLoginSisap').click()

flag = False

while not flag:
    ejecutar() 
    principal_menu = bro.find_by_id("principal-menu")
    
    if principal_menu != []:
        principal_menu.click()
        bro.click_link_by_href("/informacion-general/informacion-seniat")
        bro.click_link_by_href("#inf_accionistas")
        bro.click_link_by_href("/accionistas/gestion") 
        bro.select("id_tipo_relacion_empresa", "526")
        bro.select("id_pais","229")
        bro.fill("correo", "sucorreo@gmail.com")
        bro.fill("cantidad_acciones","1234")
        #bro.find_by_id("btnAccionistas").mouse_over()
        flag = True
#ipdb.set_trace()
