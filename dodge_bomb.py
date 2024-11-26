import os
import random
import sys
import time

import pygame as pg

WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def get_kk_img(sum_mv: tuple[int, int], base_img: pg.Surface) -> pg.Surface:

    angle = 0
    flip_x, flip_y = False, False

    if sum_mv == (0, -5):  # 上
        angle = 90
    elif sum_mv == (0, +5):  # 下
        angle = -90
    elif sum_mv == (-5, 0):  # 左
        flip_x = True
    elif sum_mv == (+5, 0):  # 右
        pass  # デフォルトは右向き
    elif sum_mv == (-5, -5):  # 左上
        angle = 45
        flip_x = True
    elif sum_mv == (-5, +5):  # 左下
        angle = -45
        flip_x = True
    elif sum_mv == (+5, -5):  # 右上
        angle = 45
    elif sum_mv == (+5, +5):  # 右下
        angle = -45

    # 回転と反転を適用
    rotated_img = pg.transform.rotozoom(base_img, angle, 1.0)
    final_img = pg.transform.flip(rotated_img, flip_x, flip_y)
    return final_img


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数で与えられたRectが画面の中か外かを判定する
    引数：こうかとんRect or 爆弾Rect
    戻り値：真理値タプル（横，縦）／画面内：True，画面外：False
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate


def create_bomb_assets():
    """
    爆弾の拡大Surfaceリストと加速リストを生成する
    """
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]  # 加速度リスト
    for r in range(1, 11):  # 1～10倍の拡大Surfaceを準備
        bb_img = pg.Surface((20 * r, 20 * r), pg.SRCALPHA)
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)
        bb_imgs.append(bb_img)
    return bb_imgs, bb_accs


def game_over(screen, kk_rct):
    black_surf = pg.Surface((WIDTH, HEIGHT))
    black_surf.fill((0, 0, 0))
    #まず黒い画面にしてから透過しているのであっていると思う
    black_surf.set_alpha(200)  
    screen.blit(black_surf, (0, 0))

    # 泣いているこうかとん画像を表示
    cry_img = pg.image.load("fig/8.png")
    cry_rct = cry_img.get_rect(center=(WIDTH / 2 - 150, HEIGHT / 2))
    cry_rct2 = cry_img.get_rect(center=(WIDTH / 2 + 150, HEIGHT / 2))
    screen.blit(cry_img, cry_rct)
    screen.blit(cry_img, cry_rct2)

    # "Game Over"の文字列を表示
    font = pg.font.Font(None, 50)  
    text = font.render("Game Over", True, (255, 255, 255))  
    text_rct = text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    screen.blit(text, text_rct)

    pg.display.update()
    time.sleep(5)  # 5秒間表示


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_imgs, bb_accs = create_bomb_assets()  # 爆弾のリストを作成
    bb_rct = bb_imgs[0].get_rect()
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +5, +5  # 爆弾速度ベクトル

    clock = pg.time.Clock()
    tmr = 0

    

    while True:
        key_lst = pg.key.get_pressed()  # キー入力状態を取得
        sum_mv = [0, 0]
        for key, tpl in DELTA.items():
            if key_lst[key]:  # 押されているキーの方向を加算
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]

        # こうかとんの向きを更新
        kk_img = get_kk_img((0, 0))
        kk_img = get_kk_img(tuple(sum_mv))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        if kk_rct.colliderect(bb_rct):
            game_over(screen, kk_rct)
            return  # ゲームオーバー

        screen.blit(bg_img, [0, 0])

        # こうかとんの移動
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, tpl in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        # 爆弾の拡大・加速
        idx = min(tmr // 500, 9)  # 段階を決定
        bb_img = bb_imgs[idx]
        acc = bb_accs[idx]
        avx = vx * acc
        avy = vy * acc

        bb_rct.move_ip(avx, avy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
        bb_rct = bb_img.get_rect(center=bb_rct.center)  # 拡大時の位置補正
        screen.blit(bb_img, bb_rct)

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
