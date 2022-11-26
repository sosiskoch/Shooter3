from pygame import *
from random import randint
import time as tm

missed = 0  # Пропущено врагов
win = 0  # Сбито
hp = 20 # Жизни
TO_WIN = 70 # Очки для победы
TO_LOOSE = 20  # Очки для поражения
W_W = 700
W_H = 500

window = display.set_mode((W_W, W_H))
display.set_caption("Шутер")
background = image.load("galaxy.jpg")
background = transform.scale(background, (W_W, W_H))
font.init()
fnt = font.Font(None, 36)
fnt_gameover = font.Font(None, 70)

mixer.init()
mixer.music.load("space.ogg")
mixer.music.play(-1)

clock = time.Clock()

class GameSprite(sprite.Sprite):
    def __init__(self, fn, x, y, w, h, speed):
        super().__init__()
        self.image = image.load(fn)
        self.image = transform.scale(self.image, (w, h))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.w = w
        self.h = h
        self.speed = speed
    def update(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def update(self):
        key_pressed = key.get_pressed()
        if key_pressed[K_d] and self.rect.x + self.w + self.speed < W_W:
            self.rect.x += self.speed
        elif key_pressed[K_a] and self.rect.x - self.speed > 0:
            self.rect.x -= self.speed
        super().update()

class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        super().update()
    def reset(self):
        self.rect.y = 0
        self.rect.x = randint(0, W_H-80)

class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()
        super().update()

def text(txt, color, coord, rf=fnt):
    img = rf.render(
        txt, # Что писать
        1,
        color # Цвет
    )
    if coord == "center":
        img_rect = img.get_rect()
        coord = ((W_W - img_rect.width) // 2, (W_H - img_rect.height) // 2)
    window.blit(img, coord)

rocket = Player("rocket.png", 325, 410, 72, 90, 5)
bullets = sprite.Group()
enemies = sprite.Group()
for i in range(5):  # [0, 1, 2, 3, 4]
    enemy = Enemy("ufo.png", 0, 0, 80, 50, i+1)
    enemy.reset()
    enemies.add(enemy)
asteroids = sprite.Group()
for i in range(2):
    asteroid = Enemy("asteroid.png", 0, 0, 80, 50, i+1)
    asteroid.reset()
    asteroids.add(asteroid)

game_over = False
is_gameplay = True
ammo = 11
reload_time = None
while not game_over:
    clock.tick(60)

    if reload_time:
        current_time = tm.time()
        if current_time - reload_time >= 3:
            ammo = 7
            reload_time = None
    for e in event.get():
        if e.type == QUIT:
            game_over = True
        if e.type == KEYDOWN:
            if e.key == K_SPACE and is_gameplay:
                if ammo > 0:
                    bullet = Bullet("bullet.png", rocket.rect.centerx, rocket.rect.top, 10, 20, 4)
                    bullets.add(bullet)
                    ammo -= 1
                    if ammo == 0:
                        reload_time = tm.time()
    # Тут правила
    # Если пуля попадает во врага - врага в начало, пулю удалить, счет увеличить
    hit = sprite.groupcollide(enemies, bullets, False, True)
    for e in hit:
        e.reset()
        win += 1
    # Если поуля попада в астероид (проверяем после врагов), удалить пулю, счет не меняетс
    sprite.groupcollide(asteroids, bullets, False, True)
    # Если враг долетел до низа экрана, засчитываем пропуск
    for e in enemies:
        if e.rect.y > W_H:
            e.reset()
            missed += 1
    # Если астероид долетел до низа экрана, отправить его вверх
    for a in asteroids:
        if a.rect.y > W_H:
            a.reset()
    # Если ракета столкнулась с врагом, врага вверх, уменьшить жизни
    collide = sprite.spritecollide(rocket, enemies, False)
    for e in collide:
        e.reset()
        hp-=1
    # Если ракета столкнулась с астероидом, астероид вверх, уменьшить жизни
    collide = sprite.spritecollide(rocket, asteroids, False)
    for e in collide:
        e.reset()
        hp-=1
    # Правила победы и поражения
    if win >= TO_WIN or missed >= TO_LOOSE or hp==0:
        is_gameplay = False

    if is_gameplay:
        window.blit(background, (0, 0))
        rocket.update()
        enemies.update()
        asteroids.update()
        bullets.update()

        text("Сбито: " + str(win), (255, 255, 255), (10, 10))
        text("Пропущено: " + str(missed), (255, 255, 255), (10, 35))
        text("Жизни: " + str(hp), (255, 255, 255), (10, 60))

        if ammo == 0:
            text("Reloading...", (255,255,255), (W_W // 2, W_H - 30))

        display.update()
    else:
        if win >= 10:
            text("YOU WIN", (0, 255, 0), "center", fnt_gameover)
        else:
            text("YOU LOOSE", (255, 0, 0), "center", fnt_gameover)
        display.update()