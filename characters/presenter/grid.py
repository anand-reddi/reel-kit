from PIL import Image, ImageDraw
def grid(img, box, scale, step, path):
    c = img.convert("RGB").crop(box); c = c.resize((int(c.width * scale), int(c.height * scale)), Image.LANCZOS); d = ImageDraw.Draw(c)
    for x in range(box[0] - box[0] % step, box[2], step):
        X = (x - box[0]) * scale; d.line([(X, 0), (X, c.height)], fill=(0, 200, 0)); d.text((X + 2, 2), str(x), fill=(0, 90, 0))
    for y in range(box[1] - box[1] % step, box[3], step):
        Y = (y - box[1]) * scale; d.line([(0, Y), (c.width, Y)], fill=(0, 200, 0)); d.text((2, Y + 2), str(y), fill=(0, 90, 0))
    c.save(path)
