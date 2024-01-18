import pygame as pg
import math
import json

class Character:
    def __init__(self,position,body_img,foot_img,bow_img,star_img,sc_size):
        self.body_position=pg.Vector2(position)
        self.body_img=pg.image.load(body_img)
        self.body_size=pg.Vector2(self.body_img.get_rect().size)
        self.foot_img=pg.image.load(foot_img)
        self.foot_size=pg.Vector2(self.foot_img.get_rect().size)
        self.bow_img=pg.image.load(bow_img)
        self.bow_size=pg.Vector2(self.bow_img.get_rect().size)
        self.rotated_bow_size=self.bow_size
        self.star_img=pg.image.load(star_img)
        self.star_size=pg.Vector2(self.star_img.get_rect().size)
        self.fook_display=False
        self.fook_position=pg.Vector2([0,0])
        self.fook_length=0
        self.body_acceleration=pg.Vector2([0,0])
        self.body_position_adjust=-self.body_position+sc_size/2
    
    def foot_position_calculate(self,frameS):
        self.foot_position_var=pg.Vector2(math.cos(frameS),math.sin(frameS))
        self.foot_positionR=self.body_position+pg.Vector2([18,32])+self.foot_position_var*4
        self.foot_positionL=self.body_position+pg.Vector2([4,32])+self.foot_position_var*-4

    def bow_position_calculate(self):
        #self.bow_angle=self.direction_calculate(self.body_position+self.body_size/2,mouse_pos)
        self.bow_position=self.body_position+self.body_size/2-self.bow_size/2+pg.Vector2(12,0).rotate(self.bow_angle)
        self.bow_img_display=pg.transform.rotate(self.bow_img,-self.bow_angle)

    def bow_angle_calculate(self,mouse_pos):
        self.bow_angle=self.direction_calculate(self.body_position+self.body_size/2-self.body_position_adjust,mouse_pos)

    def star_display(self,pos,sc): 
        sc.blit(self.star_img,pos)

    def fook_shot(self,sc_size,st):
        for i in range(4):
            self.fook_calculate()
            self.fook_length+=16
            if self.is_outside_screen(self.fook_position-self.body_position_adjust,pg.Vector2([2,2]),sc_size):
                self.fook_situation="roll"
                break
            #elif self.collision_detection(self.fook_position,pg.Vector2([2,2]),pg.Vector2(st[0][0:2]),pg.Vector2(st[0][2:4])-pg.Vector2(st[0][0:2])):
            elif self.on_ground(self.fook_position,pg.Vector2([2,2]),st):
                self.fook_situation="hold"
                self.on_ground(self.fook_position,pg.Vector2([2,2]),st)
                break

    def fook_roll(self):
        self.fook_calculate()
        self.fook_length-=60
        if self.fook_length<60:
            self.fook_display=False

    def fook_calculate(self):
        self.fook_position=self.bow_position+self.rotated_bow_size/2+pg.Vector2(self.fook_length,0).rotate(self.bow_angle)

    def fook_hold(self,mouse_L,mouse_R):
        self.bow_angle_calculate(self.fook_position-self.body_position_adjust)
        if mouse_L:
            self.body_position-=pg.Vector2([0,1])
            self.body_acceleration+=pg.Vector2([2,0]).rotate(self.bow_angle)
            self.fook_length=(self.fook_position-self.body_position-self.body_size/2)
        elif mouse_R:
            self.fook_length=(self.fook_position-self.body_position-self.body_size/2).length()
            self.fook_situation="roll"

    def fook_draw(self,sc):
        pg.draw.line(sc,(154,98,41),self.bow_position+self.rotated_bow_size/2-self.body_position_adjust,self.fook_position-self.body_position_adjust,2)

    def is_outside_screen(self,pos,size,sc_size):
        return pos.x<0 or pos.y<0 or pos.x+size.x>sc_size[0] or pos.y+size.y>sc_size[1]

    def direction_calculate(self,A_pos,B_pos):
        #A2B
        return pg.Vector2([0,0]).angle_to(B_pos-A_pos)

    def body_move(self,sc_size,st):
        self.body_position+=self.body_acceleration
        self.on_ground(self.body_position,self.body_size,st)

    def body_walk(self,L,R,st):
        if L:
            if self.body_acceleration.x>-6 or self.body_acceleration.x>0:
                self.body_acceleration-=pg.Vector2(0.5,0)
        elif R:
            if self.body_acceleration.x<6 or self.body_acceleration.x<0:
                self.body_acceleration+=pg.Vector2(0.5,0)
        elif self.on_ground(self.body_position,self.body_size,st):
            if abs(self.body_acceleration.x)<0.1:
                self.body_acceleration.x=0
            # elif self.body_acceleration.x>0:
            #     #self.body_acceleration-=pg.Vector2(0.25,0)
            #     self.body_acceleration*=-0.99
            # else:
            #     #self.body_acceleration+=pg.Vector2(0.25,0)
            #     self.body_acceleration*=0.99

    def body_drop(self,U,st):
        if self.on_ground(self.body_position,self.body_size,st):
            if U:
                self.body_acceleration-=pg.Vector2([0,10])
        else:
            self.body_acceleration+=pg.Vector2([0,1])

    def on_ground(self,A_pos,A_size,st):
        A_pos+=pg.Vector2([0,1])
        all_cd=False
        for i in st:
            st_position=pg.Vector2(i[0:2])
            st_size=pg.Vector2(i[2:4])-pg.Vector2(i[0:2])
            xy=self.xy_detection(A_pos,A_size,st_position,st_size)
            cd=self.collision_detection(A_pos,A_size,st_position,st_size)
            all_cd=all_cd or cd
            if cd:
                if xy[0]=="x":
                    A_pos.x+=xy[1]*xy[2]
                    self.body_acceleration.x=0
                    self.body_acceleration*=0.95
                elif xy[0]=="y":
                    A_pos.y+=xy[1]*xy[2]
                    self.body_acceleration.y=0
                    self.body_acceleration*=0.95
        if not all_cd:
            A_pos-=pg.Vector2([0,1])
        return all_cd
        

    def collision_detection(self,A_pos,A_size,B_pos,B_size):
        return (
            A_pos.x<B_pos.x+B_size.x and
            A_pos.x+A_size.x>B_pos.x and
            A_pos.y<B_pos.y+B_size.y and
            A_pos.y+A_size.y>B_pos.y
        )

    def xy_detection(self,A_pos,A_size,B_pos,B_size):
        difference=[abs(B_pos.x+B_size.x-A_pos.x),abs(A_pos.x+A_size.x-B_pos.x),
                    abs(B_pos.y+B_size.y-A_pos.y),abs(A_pos.y+A_size.y-B_pos.y)]
        xy=("x","x","y","y")
        pm=(1,-1,1,-1)
        index=difference.index(min(difference))
        return [xy[index],min(difference),pm[index]]

def main():
    pg.init()
    pg.display.set_caption("フックショットアドべンチャー")
    screen_size=pg.Vector2((720,480))
    screen=pg.display.set_mode(screen_size)
    game_clear=False
    exit_Flag=False
    mouse_Flag_L=False
    frame=0
    Key_L=False
    Key_R=False
    font=pg.font.Font(None,60)
    img_path="image/product/"
    flag_img=pg.image.load(f"{img_path}flag.png")
    flag_size=pg.Vector2(flag_img.get_rect().size)
    flag_position=pg.Vector2([2704,-1086])
    game_clear_text=font.render(f"GAME CLEAR",True,(0,0,0))
    me=Character((100,100),img_path+"body.png",img_path+"foot.png",img_path+"bow.png",img_path+"star.png",screen_size)

    with open("json/stage.json","r") as file:
        stage=json.load(file)
    
    dart_img=pg.image.load(img_path+"dart.png")
    dart_size=pg.Vector2(dart_img.get_rect().size)
    ground_img=pg.image.load(img_path+"ground.png")
    ground_size=pg.Vector2(ground_img.get_rect().size)

    me.foot_position_calculate(0)

    while not exit_Flag:
        mouse_Flag_R=False
        for event in pg.event.get():
            if event.type==pg.QUIT:
                exit_Flag=True
            
            elif event.type==pg.MOUSEBUTTONDOWN:
                if event.button==1:
                    mouse_Flag_L=True
                    if not me.fook_display:
                        me.fook_display=True
                        me.fook_situation="shot"
                        me.rotated_bow_size=pg.Vector2(me.bow_img_display.get_rect().size)
                        me.fook_length=0
                elif event.button==3:
                    mouse_Flag_R=True
            
            elif event.type==pg.MOUSEBUTTONUP:
                if event.button==1:
                    mouse_Flag_L=False
            
            keys = pg.key.get_pressed()
            Key_L=True if keys[pg.K_LEFT] else False
            Key_R=True if keys[pg.K_RIGHT] else False
            Key_U=True if keys[pg.K_UP] else False
            
            mouse_position=pg.Vector2(pg.mouse.get_pos())
        
        screen.fill(pg.Color("#44FFFF"))
        
        #me.body_position_adjust=me.body_position-screen_size/2
        if me.fook_display:
            if me.fook_situation=="shot":
                me.fook_shot(screen_size,stage)
                me.body_walk(Key_L,Key_R,stage)
                me.body_drop(Key_U,stage)
            elif me.fook_situation=="roll":
                me.fook_roll()
                me.body_walk(Key_L,Key_R,stage)
                me.body_drop(Key_U,stage)
            elif me.fook_situation=="hold":
                if not mouse_Flag_R:
                    me.body_walk(Key_L,Key_R,stage)
                    me.body_drop(Key_U,stage)
                me.fook_hold(mouse_Flag_L,mouse_Flag_R)
            #me.fook_draw(screen,screen_size)
        else:
            me.bow_angle_calculate(mouse_position)
            me.body_walk(Key_L,Key_R,stage)
            me.body_drop(Key_U,stage)
        if me.collision_detection(me.body_position,me.body_size,flag_position,flag_size):
            game_clear=True
        me.body_move(screen_size,stage)
        me.bow_position_calculate()
        me.foot_position_calculate(me.body_position.x/8)

        #print(me.collision_detection(me.body_position,me.body_size,pg.Vector2(stage[0][0:2]),pg.Vector2(stage[0][2:4])))

        me.body_position_adjust=me.body_position-screen_size/2-pg.Vector2([0,64])
        if me.fook_display:
            me.fook_draw(screen)

        for i in stage:
            width=int((i[2]-i[0])/64)
            height=int((i[3]-i[1])/64)
            for n in range(width):
                for j in range(height):
                    if j==0:
                        screen.blit(dart_img,pg.Vector2(i[0]+n*64,i[1]+j*64)-me.body_position_adjust)
                    else:
                        screen.blit(ground_img,pg.Vector2(i[0]+n*64,i[1]+j*64)-me.body_position_adjust)

        screen.blit(me.body_img,me.body_position-me.body_position_adjust)
        screen.blit(me.foot_img,me.foot_positionR-me.body_position_adjust)
        screen.blit(me.foot_img,me.foot_positionL-me.body_position_adjust)
        screen.blit(me.bow_img_display,me.bow_position-me.body_position_adjust)
        if game_clear:
            screen.blit(game_clear_text,pg.Vector2([225,100]))
        else:
            screen.blit(flag_img,flag_position-me.body_position_adjust)
        
        #pg.draw.line(screen,(154,98,41),pg.Vector2([0,0]),pg.Vector2([100,100]),2)
        
        pg.display.flip()
        
        if me.body_position.y>960:
            me.body_position=pg.Vector2([100,100])
            me.body_acceleration=pg.Vector2([0,0])
            me.fook_display=False
            game_clear=False

        frame+=1
        pg.time.Clock().tick(30)
    
    pg.quit()

if __name__=="__main__":
    main()