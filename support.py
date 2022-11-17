import pygame
from os import walk


def import_folder(path):
    surface_list = []

    # folder_name, sub_folder, img_list
    for _, __, img_lists in walk(path):
        for img in img_lists:
            full_path = path + '/' + img
            image_surface = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surface)

    return surface_list
