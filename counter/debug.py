import os

from PIL import ImageDraw, ImageFont


def draw(predictions, image, image_name):
    draw_image = ImageDraw.Draw(image, "RGBA")

    image_width, image_height = image.size

    font = ImageFont.truetype("counter/resources/arial.ttf", 20)
    i = 0
    for prediction in predictions:
        box = prediction.box
        draw_image.rectangle(
            [(box.xmin * image_width, box.ymin * image_height),
             (box.xmax * image_width, box.ymax * image_height)],
            outline='red')
        class_name = prediction.class_name
        draw_image.text(
            (box.xmin * image_width, box.ymin * image_height - font.getlength(class_name)),
            f"{class_name}: {prediction.score}", font=font, fill='black')
        i += 1
    try:
        os.mkdir('tmp/debug')
    except OSError:
        pass
    image.save(f"tmp/debug/{image_name}", "JPEG")
