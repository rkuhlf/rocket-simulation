import pygame
import pandas as pd
import numpy as np # definitely overkill

pygame.init()

display_width = 800
display_height = 600

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('Rockets')

black = (0,0,0)
white = (255,255,255)

clock = pygame.time.Clock()

rocket_image = pygame.image.load('rocket.png')
rocket_image = pygame.transform.scale(rocket_image, (50, 30))



position_data = pd.read_csv("output.csv", dtype={'x': float, 'y': float, 'x_acc': float, 'y_acc': float})

position_data['y'] *= display_height / 1000


def rocket(x,y):
  # print(rocket_image)
  gameDisplay.blit(rocket_image, (x,y))


while True:
  for index, row in position_data.iterrows():
    gameDisplay.fill(black)

    print(row['y'])
    rocket(row['x'], display_height - row['y'])
        
    pygame.display.update()
    clock.tick(60)

pygame.quit()
quit()
