import pygame

class Cell:

    QUIET = 0
    MOVE = 1
    FIGHT = 2
    WAIT = 3

    DAMAGE_STAGE_0 = 1_000
    DAMAGE_STAGE_1 = 1_001
    DAMAGE_STAGE_2 = 1_002
    DAMAGE_STAGE_3 = 1_003
    BAD_ADD = 1_000

    DAMAGE_STAGE_0_COLOR = (255, 255, 255)
    DAMAGE_STAGE_0_COLOR_BAD = (122, 106, 106)
    DAMAGE_STAGE_1_COLOR = (225, 170, 170)
    DAMAGE_STAGE_1_COLOR_BAD = (95, 90, 115)
    DAMAGE_STAGE_2_COLOR = (190, 85, 85)
    DAMAGE_STAGE_2_COLOR_BAD = (65, 70, 120)
    DAMAGE_STAGE_3_COLOR = (158, 0, 0)
    DAMAGE_STAGE_3_COLOR_BAD = (40, 50, 130)

    def __init__(self, x, y, pattern, good):
        self.x = x
        self.y = y
        self.good = good
        self.pattern = pattern.copy()  # Lista de tuplas (dx, dy)
        self.pattern_0 = ""
        for key in operacion.PATTERNS.keys():
            if operacion.PATTERNS.get(key) == pattern:
                self.pattern_0 = key
        print(self.pattern_0)
        self.next_move = self.MOVE
        self.damage_bitmap = []
        for xy in pattern:
            self.damage_bitmap.append(self.DAMAGE_STAGE_0)
        

    def draw(self, world):
        counter = 0
        for dx, dy in self.pattern:   
            value = self.damage_bitmap[counter]
            if not self.good:
                value += self.BAD_ADD
            world.write(self.x + dx, self.y + dy, value)
            counter += 1

    def erase(self, world):
        for dx, dy in self.pattern:
            world.write(self.x + dx, self.y + dy, world.DEAD)

    def move_left(self):
        self.x -= 1

    def move_right(self):
        self.x += 1

    def detect_cells(self, good_cells, enemies) -> int:
        if self.good:
            for i in range (len(good_cells)):
                cell = good_cells[i]
                cell_x = cell.x
                x_diff = cell_x - self.x - max(dx for dx,dy in self.pattern)
                if x_diff == 0:
                    continue
                elif x_diff <= 2 and x_diff > 0:
                    self.next_move = Cell.QUIET
                    return 0
                elif self.next_move != Cell.WAIT:
                    self.next_move = Cell.MOVE
            return 0
        else:
            cells = good_cells + enemies
            for i in range(len(cells)):
                cell = cells[i]
                cell_x = cell.x + max(dx for dx, dy in cell.pattern)
                cell_good = cell.good
                self_x = self.x
                self_pattern = self.pattern
                x_diff = self.x - cell_x
                if x_diff == 2:
                    self.next_move = Cell.QUIET
                    return 0
                elif cell in good_cells:
                    if x_diff == 1:
                        self.next_move = Cell.FIGHT
                        cell.next_move = Cell.FIGHT
                        return i
            self.next_move = Cell.MOVE
            return 0

    def is_offscreen(self):
        return self.x == 0  or self.x + max(dx for dx,dy in self.pattern) == operacion.WIDTH

    def cells_fight(good_cell, bad_cell) -> any:
        
        good_cell_warriors = 0
        good_cell_max_x = max(dx for dx,dy in good_cell.pattern)
        for i in range(len(good_cell.pattern) -1, -1, -1):
            if (good_cell.pattern[i][0] < good_cell_max_x):
                break
            good_cell_warriors += 1
        
        bad_cell_warriors = 0
        for i in range(len(bad_cell.pattern)):
            if bad_cell.pattern[i][0] > 0:
                break
            bad_cell_warriors += 1

        to_erase = []

        if good_cell_warriors > bad_cell_warriors:
            
            for w in range(bad_cell_warriors):
                point = bad_cell.pattern.pop(0)
                bad_cell.damage_bitmap.pop(0)
                to_erase.append((bad_cell.x + point[0], bad_cell.y + point[1]))
            for p in range(len(bad_cell.pattern)):
                point = bad_cell.pattern[p]
                x = point[0]
                y = point[1]
                bad_cell.pattern.pop(p)
                bad_cell.pattern.insert(p, (x - 1, y))
            bad_cell.x += 1

            damage_counter = bad_cell_warriors
            i = len(good_cell.pattern) - 1
            while damage_counter > 0:
                iDamage = good_cell.damage_bitmap[i]
                if iDamage + damage_counter <= Cell.DAMAGE_STAGE_3:
                    good_cell.damage_bitmap[i] += damage_counter
                    damage_counter = 0
                else:
                    damage_counter -= Cell.DAMAGE_STAGE_3 + 1 - iDamage
                    point = good_cell.pattern[i]
                    to_erase.append((good_cell.x + point[0], good_cell.y + point[1]))
                    good_cell.pattern.pop(i)
                    good_cell.damage_bitmap.pop(i)
                    i-=1
            
            good_cell.next_move = Cell.WAIT
        
        if bad_cell_warriors > good_cell_warriors:

            for w in range(good_cell_warriors):
                point = good_cell.pattern.pop()
                good_cell.damage_bitmap.pop()
                to_erase.append((good_cell.x + point[0], good_cell.y + point[1]))
            
            damage_counter = good_cell_warriors
            i = 0
            while damage_counter > 0:
                iDamage = bad_cell.damage_bitmap[i]
                if iDamage + damage_counter <= Cell.DAMAGE_STAGE_3:
                    bad_cell.damage_bitmap[i] += damage_counter
                    damage_counter = 0
                else:
                    damage_counter -= Cell.DAMAGE_STAGE_3 + 1 - iDamage
                    point = bad_cell.pattern[i]
                    to_erase.append((bad_cell.x + point[0], bad_cell.y + point[1]))
                    bad_cell.pattern.pop(i)
                    bad_cell.damage_bitmap.pop(i)
                    i-=1
            
            bad_cell.next_move = Cell.QUIET
            if good_cell.pattern != []:
                good_cell.next_move = Cell.WAIT
        
        if good_cell_warriors == bad_cell_warriors:

            good_cell_damage = good_cell.damage_bitmap[-1]
            bad_cell_damage = bad_cell.damage_bitmap[0]

            if good_cell_damage == bad_cell_damage:
                for w in range(good_cell_warriors):
                    good_point = good_cell.pattern.pop()
                    good_cell.damage_bitmap.pop()
                    bad_point = bad_cell.pattern.pop(0)
                    bad_cell.damage_bitmap.pop(0)
                    to_erase.append((good_point[0] + good_cell.x, good_point[1] + good_cell.y))
                    to_erase.append((bad_point[0] + bad_cell.x, bad_point[1] + bad_cell.y))
                for p in range(len(bad_cell.pattern)):
                    point = bad_cell.pattern[p]
                    x = point[0]
                    y = point[1]
                    bad_cell.pattern.pop(p)
                    bad_cell.pattern.insert(p, (x - 1, y))
                bad_cell.x += 1
                
                if good_cell.pattern != []:
                    good_cell.next_move = Cell.WAIT
            elif good_cell_damage < bad_cell_damage:
                for w in range(bad_cell_warriors):
                    point = bad_cell.pattern.pop(0)
                    bad_cell.damage_bitmap.pop(0)
                    to_erase.append((bad_cell.x + point[0], bad_cell.y + point[1]))
                for p in range(len(bad_cell.pattern)):
                    point = bad_cell.pattern[p]
                    x = point[0]
                    y = point[1]
                    bad_cell.pattern.pop(p)
                    bad_cell.pattern.insert(p, (x - 1, y))
                bad_cell.x += 1
                for w in range(good_cell_warriors - 1):
                    point = good_cell.pattern.pop()
                    good_cell.damage_bitmap.pop()
                    to_erase.append((good_cell.x + point[0], good_cell.y + point[1]))
                good_cell.damage_bitmap[-1] += Cell.DAMAGE_STAGE_3 + 1 - bad_cell_damage
                
                good_cell.next_move = Cell.WAIT
            elif good_cell_damage > bad_cell_damage:
                for w in range(good_cell_warriors):
                    point = good_cell.pattern.pop()
                    good_cell.damage_bitmap.pop()
                    to_erase.append((good_cell.x + point[0], good_cell.y + point[1]))
                for w in range(bad_cell_warriors - 1):
                    point = bad_cell.pattern.pop(0)
                    bad_cell.damage_bitmap.pop(0)
                    to_erase.append((bad_cell.x + point[0], bad_cell.y + point[1]))
                bad_cell.damage_bitmap[0] += Cell.DAMAGE_STAGE_3 + 1 - good_cell_damage
                
                if good_cell.pattern != []:
                    good_cell.next_move = Cell.WAIT
            
            bad_cell.next_move = Cell.QUIET

        
        return to_erase

class operacion:
    PATTERNS = {
    "1": [(0,1)],
    "2": [(0,0), (0,1), (0,2), (1,1)],
    "3": [(0,1), (1,1)],
    "4": [(0,0), (0,1), (0,2)],
    "5": [(0,2), (1,1), (2,0)],
    "6": [(0,0), (1,1), (2,2)],
    "7": [(0, 0), (0, 1), (1, 0), (1, 1)],
    "8": [(0,1), (1,0)],
    "9": [(0,0), (0,1), (0,2), (1,2)],
    "10": [(0,0), (0,1), (0,2), (1,2), (1,1)],
    "11": [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 0), (2, 1), (2, 2)]
    }

    WIDTH = 40 # ANCHO DE LAS CELDAS
    HEIGHT = 20 # ALTO DE LAS CELDAS
    LIVE = 1 # VALOR CELDA VIVA
    DEAD = 0 # VALOR CELDA MUERTA



    __world = [] # lista donde cada valor corresponde al estado de una celda, ESTADO PRINCIPAL
    __next = [] # lista de respaldo, cuando hacemos el paso de una iteración a la siguiente

    __born = [] #lista de numeros de celdas vecinas activas para que una celda se active
    __alive = [] # lista de numero de celdas vecinas activas para que una celda se mantenga activa

    __iterations = 0 #contador de iteraciones
    
    #constructor
    #formato basico del juego de la vida de conway

    def insert_pattern(self, pattern_name: str, x: int, y: int) -> None:
     if pattern_name in self.PATTERNS:
        for dx, dy in self.PATTERNS[pattern_name]:
            self.write(x + dx, y + dy, self.LIVE)



    def __init__(self, pattern: str = "23/3"):  # Pattern por defecto 23/3 
        self.reset()
        self.__alive = [int(v) for v in pattern.split("/")[0]] #2.3
        self.__born = [int(v) for v in pattern.split("/")[1]] #3

    @property #propiedades
    def iterations(self) -> int:
        return self.__iterations #devuelve el numero de iteraciones procesadas

    @property
    def livecells(self) -> int:
        return self.__world.count(1) #devuelve el numero de celdas activas en el espacio

    def reset (self): #inicializa las listas con ceros
        self.__iterations = 0
        self.__world = [0] * (self.WIDTH * self.HEIGHT)
        self.__next = [0] * (self.WIDTH * self.HEIGHT)

    def read(self, x: int, y: int) -> int:
        # permite obtener el estado de una celda con sus cordenadas x y y, accediendo a la lista world
        # retorna el valor de la celda activa o inactiva (esos son los estados que tiene el juego de la vida)
        if x >= self.WIDTH:
            x-= self.WIDTH

        elif x < 0:
            x+= self.WIDTH

        if y >= self.HEIGHT:
            y -= self.HEIGHT

        elif y < 0:
            y += self.HEIGHT

        return self.__world[(y * self.WIDTH) + x]

    def write(self, x: int, y: int, value: int) -> None: #establece el valor de una celda teniendo en cuenta sus coordenadas. 
        self.__world[(y * self.WIDTH) + x] = value

    def update(self) -> None:
        self.__iterations += 1  # Incrementa el contador de iteraciones

            
    def draw(self, context: pygame.Surface) -> None:
        cell_size = 25  # cuadrado: 25 x 25

        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                current = self.read(x, y)
                rect = (x * cell_size, y * cell_size, cell_size, cell_size)
                color = ()
                if current == Cell.DAMAGE_STAGE_0:
                    color = Cell.DAMAGE_STAGE_0_COLOR
                elif current == Cell.DAMAGE_STAGE_1:
                    color = Cell.DAMAGE_STAGE_1_COLOR
                elif current == Cell.DAMAGE_STAGE_2:
                    color = Cell.DAMAGE_STAGE_2_COLOR
                elif current == Cell.DAMAGE_STAGE_3:
                    color = Cell.DAMAGE_STAGE_3_COLOR
                elif current == Cell.DAMAGE_STAGE_0 + Cell.BAD_ADD:
                    color = Cell.DAMAGE_STAGE_0_COLOR_BAD
                elif current == Cell.DAMAGE_STAGE_1 + Cell.BAD_ADD:
                    color = Cell.DAMAGE_STAGE_1_COLOR_BAD
                elif current == Cell.DAMAGE_STAGE_2 + Cell.BAD_ADD:
                    color = Cell.DAMAGE_STAGE_2_COLOR_BAD
                elif current == Cell.DAMAGE_STAGE_3 + Cell.BAD_ADD:
                    color = Cell.DAMAGE_STAGE_3_COLOR_BAD

                if color != ():
                    pygame.draw.rect(surface=context, color=color, rect=rect)
                else:
                    pygame.draw.rect(surface=context, color=(64, 64, 64), rect=rect, width=1)

    #Funciones para guardar y cargar el estado del juego
    def save(self, filename:str) -> None:
        with open(filename, mode="w", encoding="utf-8") as fp:
            fp.write(str(self.__world))
    
    def load(self, filename:str) -> None:
        with open(filename, mode="r", encoding="utf-8") as fp:
            data = fp.read()[1:-1]
            self.__world = [int(v) for v in data.split(",")]

