import sys, pygame
import tkinter as tk
from tkinter import filedialog
from operacion import Cell
from random import Random

key_patterns = {
    pygame.K_1: "1",
    pygame.K_2: "2",
    pygame.K_3: "3",
    pygame.K_4: "4",
    pygame.K_5: "5",
    pygame.K_6: "6", 
    pygame.K_7: "7",
    pygame.K_8: "8",
    pygame.K_9: "9",
    pygame.K_0: "10",
    pygame.K_u: "11"
}


import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

root = tk.Tk()
root.withdraw()

from operacion import operacion

size = width, height = 1000, 564 # ancho y alto de los pixeles en la ventana
bottom_bar_height = 64 #ancho de la barra de botones

black = (0,0,0)
white = (255, 255, 255)
gray = (92, 92, 92)

#Funcion para cambiar estado de las celdas
def mouse_click(world: operacion, mouse_x: int, mouse_y: int) -> None: 
    x = int(mouse_x / 25)
    y = int(mouse_y / 25)
    if world.read(x,y) == world.LIVE:
        world.write(x,y,world.DEAD)
    else:
        world.write(x, y, world.LIVE)
        #ENEMIGOS

#Termina enemigos
def main():
#inicializacion de la libreria
    pygame.init()
    #MODIFICADO
    enemy_pattern = [
[(0, 0), (1, 0),
(0, 1),
(1, 2), (2, 2)
],
[
 (0,0),(0,1),       
 (1,0),(1,1),
 (2,0)        
    ]]
    #TERMINA MODIFICACION
    pygame.font.init()
    world = operacion()

    #inicialización de la ventana
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("OPERACIÓN PATÓGENA")
    
    #iniciación de la imagen de fondo
    play = pygame.image.load("play.png")
    play = pygame.transform.scale(play, (50, 50))   
    playrect = play.get_rect()
    playrect = playrect.move(400, 505)

    pause = pygame.image.load("pause.png")
    pause = pygame.transform.scale(pause, (50, 50))
    pauserect = pause.get_rect()
    pauserect = pauserect.move(468, 505)

    clear = pygame.image.load("clear.png")
    clear = pygame.transform.scale(clear, (50, 50))
    clearrect = clear.get_rect()
    clearrect = clearrect.move(532, 505)

    load = pygame.image.load("load.png")
    load = pygame.transform.scale(load, (50, 50))
    loadrect = load.get_rect()
    loadrect = loadrect.move(596, 505)

    save = pygame.image.load("save.png")
    save = pygame.transform.scale(save, (50, 50))
    saverect = save.get_rect()
    saverect = saverect.move(660, 505 )

    myfont = pygame.font.SysFont('lucida Console', 30)

    running = False  
    game_over=False
    #MODIFICADO 
    good_cells = [[], [], [], []] 
    enemies = [[], [], [], []]

    enemy_spawn_timer = 0

    cell_put_on_it = False
    #TERMINA MODIFICACION
    #bucle de ejecución
    while 1:
        for event in pygame.event.get():
            cell_put_on_it = False
            
            def reset():
                world.reset()
                screen.fill(black)
                world.draw(screen)
                for cells_list in good_cells + enemies:
                    cells_list.clear()
                enemy_spawn_timer = 0

            #Evento cerrar ventana
            if event.type == pygame.QUIT:
                print("END...")
                sys.exit()
                
            #Evento de click del ratón
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if y <= 500:
                    mouse_click(world, x, y)
                else:
                    if playrect.collidepoint(x,y):
                        running = True
                    if pauserect.collidepoint(x,y):
                        running = False
                    if clearrect.collidepoint(x,y):
                        reset()
                    if loadrect.collidepoint(x, y):
                        filepath = filedialog.askopenfilename(title="Cargar patrón", filetypes=[("Archivos de texto", "*.txt")])
                        if filepath:
                            world.load(filepath)
                    if saverect.collidepoint(x, y):
                        filepath = filedialog.asksaveasfilename(title="Guardar patrón", defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")])
                        if filepath:
                            world.save(filepath)

            if event.type == pygame.KEYDOWN: # presionar teclas para dibujar :DDD
                if event.key in key_patterns and not cell_put_on_it:

                    good_cells_len = 0
                    for sub_good_cells in good_cells:
                        good_cells_len += len(sub_good_cells)
                    
                    print(good_cells_len)
                
                    if good_cells_len < 25:

                        pattern = operacion.PATTERNS[key_patterns[event.key]].copy()

                        PATTERN_PRICE = [
                            25,
                            20,
                            15,
                            12,
                            10,
                            7,
                            4,
                            2,
                            1
                        ]

                        pattern_use = 0

                        for i in range(4):
                            for good_cell in good_cells[i]:
                                if good_cell.pattern_0 == key_patterns[event.key]:
                                    pattern_use += 1

                        if pattern_use < PATTERN_PRICE[len(pattern) - 1]:
                            mouse_y = pygame.mouse.get_pos()[1]
                            pixels_per_cell = width / operacion.WIDTH
                            cells_per_carril = 5
                            carril_height = cells_per_carril * pixels_per_cell

                            carril = min(int(mouse_y / carril_height), 3)

                            free_create_space = True
                            cs_delta = 4

                            for c in good_cells[carril] + enemies[carril]:
                                if c.x <= cs_delta:
                                    free_create_space = False
                                    break
                                

                            if free_create_space:
                                x = 0
                                if not running:
                                    x = 1
                                good_cell = Cell(x, carril * cells_per_carril + 1, pattern, True)
                                good_cells[carril].append(good_cell)
                                good_cell.draw(world)
                                cell_put_on_it = True


        #actualizacion AC
        if running and not game_over:
            world.update()
            pygame.time.delay(500) #delay de 500ms entre actualización de celdas
        # ENEMIGOS
            for i in range(4):
                for enemy in enemies[i]:
                    cell_i = enemy.detect_cells(good_cells[i], enemies[i])
                    if enemy.next_move == Cell.MOVE:
                        enemy.erase(world)
                        enemy.move_left()
                        if enemy.x <= 0:
                            running = False
                            game_over = True
                            break

                    elif enemy.next_move == Cell.FIGHT:
                        good_cell = good_cells[i][cell_i]
                        enemy.erase(world)
                        to_erase = Cell.cells_fight(good_cell, enemy)
                        if enemy.pattern == []:
                            enemies[i].remove(enemy)
                        if good_cell.pattern == []:
                            good_cells[i].pop(cell_i)
                        for x,y in to_erase:
                            world.write(x, y, world.DEAD)


            for i in range(4):
                enemies[i] = [enemy for enemy in enemies[i] if not enemy.is_offscreen()]
                #TERMINA EL JUEGO
            for i in range(4):
                for enemy in enemies [i]:
                    if enemy.x <=0:
                        running =False
                        game_over=True
                        break
                else:
                    continue
                break
            for sub_enemies in enemies:
                for enemy in sub_enemies:
                    enemy.draw(world)
               
            enemy_spawn_timer += 1
            if enemy_spawn_timer >= 5:  # cada 5 ciclos
                enemy_spawn_timer = 0
                from random import choice
                pattern = choice(list(operacion.PATTERNS.values())).copy()

                carril = Random().randint(0, 3)
                enemies[carril].append(Cell(38, carril * 5 + 1, pattern, False))  # 38*25 = 950px
    
            #CELULAS BUENAS
        
            for i in range(4):
                for good_cell in good_cells[i]:
                    if good_cell.next_move == Cell.FIGHT:
                        good_cell.erase(world)
                        continue
                    good_cell.detect_cells(good_cells[i], enemies[i])
                    if good_cell.next_move == Cell.MOVE:
                        good_cell.erase(world)
                        good_cell.move_right()
                    if good_cell.next_move == Cell.WAIT:
                        good_cell.next_move = Cell.MOVE

            for i in range(4):
                good_cells[i] = [good_cell for good_cell in good_cells[i] if not good_cell.is_offscreen()]
            
            for sub_good_cells in good_cells:
                for good_cell in sub_good_cells:
                    good_cell.draw(world)

        # refrescar
        screen.fill(black)
        world.draw(screen)

        # Dibujar los 4 carriles horizontales
        for i in range(4):
            carril_y = i * 125  # Separación vertical entre carriles (500px / 4)
            pygame.draw.rect(screen, gray, pygame.Rect(0, carril_y, 1000, 5))
            create_space_width = 2
            pygame.draw.line(screen, (0, 0, 255), (25, carril_y + 25), (100, carril_y + 25), create_space_width)
            pygame.draw.line(screen, (0, 0, 255), (25, carril_y + 25), (25, carril_y + 100), create_space_width)
            pygame.draw.line(screen, (0, 0, 255), (100, carril_y + 100), (100, carril_y + 25), create_space_width)
            pygame.draw.line(screen, (0, 0, 255), (100, carril_y + 100), (25, carril_y + 100), create_space_width)
        screen.blit(play, playrect)
        screen.blit(pause, pauserect)
        screen.blit(clear, clearrect)
        screen.blit(load, loadrect)
        screen.blit(save, saverect)

        textsurface = myfont.render("RUNNING" if running else "PAUSE", True, white)
        if game_over:
         game_over_font = pygame.font.SysFont('lucida Console', 60)
         game_over_surface = game_over_font.render("GAME OVER", True, (255, 0, 0))
         screen.fill(black)
         screen.blit(game_over_surface, (width // 2 - 160, height // 2 - 30))
         world.draw(screen)
         pygame.display.flip()
         pygame.time.wait(5000)
         game_over = False
         reset()

        screen.blit(textsurface, (100, 516))
        screen.blit(
            myfont.render(str(world.iterations), True, white), (750,516))
        pygame.display.flip()

if __name__ == "__main__":
    main()
