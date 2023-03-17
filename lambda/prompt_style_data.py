class PromptStyleData:
    def __init__(self):
        self.s3KeyMap = {
            "None": "None/None.jpeg",
            "3-D": "3-D/3-D.jpeg",
            "3-D Render": "3-D Render/3-D Render.jpeg",
            "Acrylic": "Acrylic/Acrylic.jpeg",
            "Ambient": "Ambient/Ambient.jpeg",
            "Anime": "Anime/Anime.jpeg",
            "Bronze": "Bronze/Bronze.jpeg",
            "Cartoon": "Cartoon/Cartoon.jpeg",
            "Chalk": "Chalk/Chalk.png",
            "Charcoal": "Charcoal/Charcoal.jpeg",
            "Cinematic": "Cinematic/Cinematic.jpeg",
            "Clay": "Clay/Clay.jpeg",
            "Close-Up": "Close-Up/Close-Up.jpeg",
            "Color Splash": "Color Splash/Color Splash.jpeg",
            "Colored Pencil": "Colored Pencil/Colored Pencil.jpeg",
            "Drawing": "Drawing/Drawing.jpeg",
            "Glass": "Glass/Glass.jpeg",
            "Graphite Pencil": "Graphite Pencil/Graphite Pencil.jpeg",
            "Ice": "Ice/Ice.jpeg",
            "Ink": "Ink/Ink.jpeg",
            "Long Exposure": "Long Exposure/Long Exposure.jpeg",
            "Long Shot": "Long Shot/Long Shot.jpeg",
            "Marble": "Marble/Marble.jpeg",
            "Medium Shot": "Medium Shot/Medium Shot.jpeg",
            "Metal": "Metal/Metal.jpeg",
            "Monochrome": "Monochrome/Monochrome.jpeg",
            "Natural": "Natural/Natural.jpeg",
            "Oil": "Oil/Oil.jpeg",
            "Origami": "Origami/Origami.jpeg",
            "Painting": "Painting/Painting.jpeg",
            "Panorama": "Panorama/Panorama.jpeg",
            "Pastel": "Pastel/Pastel.jpeg",
            "Photography": "Photography/Photography.jpeg",
            "Polaroid": "Polaroid/Polaroid.jpeg",
            "Portrait": "Portrait/Portrait.jpeg",
            "POV": "POV/POV.jpeg",
            "Ring": "Ring/Ring.jpeg",
            "Sand": "Sand/Sand.jpeg",
            "Soft": "Soft/Soft.jpeg",
            "Studio": "Studio/Studio.jpeg",
            "Sunlight": "Sunlight/Sunlight.jpeg",
            "Tilt-Shift": "Tilt-Shift/Tilt-Shift.jpeg",
            "Vintage": "Vintage/Vintage.jpeg",
            "Watercolor": "Watercolor/Watercolor.jpeg",
            "Wood": "Wood/Wood.jpeg"
        }

    def getObjectUrlForStyleKey(self, styleKey, bucketName):
        s3Key = self.s3KeyMap.get(styleKey)
        if not s3Key:
            return ""
        objectUrl = f"https://{bucketName}.s3.amazonaws.com/{s3Key}"
        return objectUrl

    def getPromptStyles(self, bucketName):
        promptStyles = self.getDefaultPromptStyles()
        for style in promptStyles:
            style["imageUrl"] = self.getObjectUrlForStyleKey(style["key"], bucketName)
            for substyle in style.get("substyles", []):
                for value in substyle["values"]:
                    value["imageUrl"] = self.getObjectUrlForStyleKey(value["key"], bucketName)

        return promptStyles
    

    def getDefaultPromptStyles(self):
        NONE = { "key": "None" }
        PAINTING_MEDIUMS = {
            "key": "Medium",
            "values": [
                NONE,
                {
                    "key": "Oil",
                    "prefix": "oil"
                },
                {
                    "key": "Watercolor",
                    "prefix": "watercolor"
                },
                {
                    "key": "Acrylic",
                    "prefix": "acrylic"
                }
            ]
        }
        DRAWING_MEDIUMS = {
            "key": "Medium",
            "values": [
                NONE,
                {
                    "key": "Charcoal",
                    "prefix": "charcoal"
                },
                {
                    "key": "Graphite Pencil",
                    "prefix": "graphite pencil"
                },
                {
                    "key": "Colored Pencil",
                    "prefix": "colored pencil"
                },
                {
                    "key": "Pastel",
                    "prefix": "pastel"
                },
                {
                    "key": "Chalk",
                    "prefix": "chalk"
                },
                {
                    "key": "Ink",
                    "prefix": "ink"
                }
            ]
        }
        THREE_DIMENSIONAL_MEDIUMS = {
            "key": "Medium",
            "values": [
                NONE,
                {
                    "key": "3-D Render",
                    "prefix": "3-D render",
                    "suffix": "Blender"
                },
                {
                    "key": "Clay",
                    "prefix": "Clay sculpture"
                },
                {
                    "key": "Wood",
                    "prefix": "Wood sculpture"
                },
                {
                    "key": "Metal",
                    "prefix": "Metal sculpture"
                },
                {
                    "key": "Marble",
                    "prefix": "Marble sculpture"
                },
                {
                    "key": "Bronze",
                    "prefix": "Bronze sculpture"
                },
                {
                    "key": "Origami",
                    "prefix": "Origami"
                },
                {
                    "key": "Glass",
                    "prefix": "Glass sculpture"
                },
                {
                    "key": "Ice",
                    "prefix": "Ice sculpture"
                },
                {
                    "key": "Sand",
                    "prefix": "Sand sculpture"
                }
            ]
        }
        PHOTOGRAPHY_LIGHTING_STYLES = {
            "key": "Lighting",
            "values": [
                NONE,
                {
                    "key": "Soft",
                    "suffix": "soft lighting"
                },
                {
                    "key": "Studio",
                    "suffix": "studio lighting"
                },
                {
                    "key": "Sunlight",
                    "suffix": "natural sunlight"
                },
                {
                    "key": "Cinematic",
                    "suffix": "cinematic lighting"
                },
                {
                    "key": "Natural",
                    "suffix": "natural lighting"
                },
                {
                    "key": "Ambient",
                    "suffix": "ambient lighting"
                },
                {
                    "key": "Ring",
                    "suffix": "ring lighting"
                }
            ]
        }
        PHOTOGRAPHY_STYLES = {
            "key": "Style",
            "values": [
                NONE,
                {
                    "key": "Polaroid",
                    "prefix": "polaroid"
                },
                {
                    "key": "Portrait",
                    "prefix": "portrait"
                },
                {
                    "key": "Monochrome",
                    "prefix": "monochrome"
                },
                {
                    "key": "Vintage",
                    "prefix": "vintage"
                },
                {
                    "key": "Long Exposure",
                    "prefix": "long exposure"
                },
                {
                    "key": "Color Splash",
                    "prefix": "color splash"
                },
                {
                    "key": "Tilt-Shift",
                    "prefix": "tilt-shift"
                }
            ]
        }
        PHOTOGRAPHY_SHOT_TYPES = {
            "key": "Shot Type",
            "values": [
                NONE,
                {
                    "key": "Close-Up",
                    "prefix": "close-up"
                },
                {
                    "key": "Medium Shot",
                    "prefix": "medium shot"
                },
                {
                    "key": "Long Shot",
                    "prefix": "long shot"
                },
                {
                    "key": "POV",
                    "prefix": "POV"
                },
                {
                    "key": "Panorama",
                    "prefix": "panorama"
                }
            ]
        }

        PROMPT_STYLES = [
            NONE,
            {
                "key": "Painting",
                "prefix": "painting",
                "substyles": [
                    PAINTING_MEDIUMS,
                ]
            },
            {
                "key": "Drawing",
                "prefix": "drawing",
                "substyles": [
                    DRAWING_MEDIUMS,
                ]
            },
            {
                "key": "3-D",
                "substyles": [
                    THREE_DIMENSIONAL_MEDIUMS
                ]
            },
            {
                "key": "Photography",
                "prefix": "photograph",
                "substyles": [
                    PHOTOGRAPHY_LIGHTING_STYLES,
                    PHOTOGRAPHY_STYLES,
                    PHOTOGRAPHY_SHOT_TYPES
                ]
            }
        ]

        return PROMPT_STYLES