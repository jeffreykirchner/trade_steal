
import json
import logging

def generate_css_sprite_sheet(file, static_image_url):
    '''
    take a sprite sheet json file and return css version
    '''
    logger = logging.getLogger(__name__) 
    
    css = ""

    with open(file, encoding='utf-8-sig') as f:
        data = json.load(f)

        data = dict(data)

        # logger.info(f'{data}')

        for d in data['frames']:
            frame = data['frames'][d]

            s = f'#{d}{{\n \
                        background-repeat: no-repeat; \
                        background-size: contain; \
                        background-position: center; \
                        background: url(/static/avatars.png) -{frame["frame"]["x"]}px -{frame["frame"]["y"]}px;\n \
                        width:{frame["frame"]["w"]}px;\n \
                        height:{frame["frame"]["h"]}px;\n \
                       }}\n'
            css += s


        f.close()

        # logger.info(css)

    return css.replace(".jpg", "")

