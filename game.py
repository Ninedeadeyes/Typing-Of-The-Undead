import pygame,  random,copy

from dictionary import wordlist

pygame.init()

# Load multiple zombie images at the start
zombie_images = [
    pygame.transform.scale(pygame.image.load('assets/arts/zombie1.png'), (90, 90)),
    pygame.transform.scale(pygame.image.load('assets/arts/zombie2.png'), (90, 90)),
    pygame.transform.scale(pygame.image.load('assets/arts/zombie3.png'), (90, 90)),
    pygame.transform.scale(pygame.image.load('assets/arts/zombie4.png'),(90, 90)),
    pygame.transform.scale(pygame.image.load('assets/arts/zombie5.png'), (90, 90))
]

medikit_image = pygame.image.load('assets/arts/medikit.png')
medikit_image = pygame.transform.scale(medikit_image, (50, 50))

#We’re getting ready to track where each word length starts:

len_indexes = []  #will store the positions in the list where the word length increases.
length = 1      # means we’re starting with 1-letter words.

# wordlist sorting mechanism 

wordlist.sort(key=len)  # This sorts the whole list so that short words come first and long words come last.
                        # eg ["a", "I", "to", "be", "apple" etc etc

for i in range(len(wordlist)):  #This loop goes through every word in the list.
    if len(wordlist[i])>length:  
        length+=1
        len_indexes.append(i)  #we save the position i in len_indexes — this marks where words of a new length start.
                                # eg:print(len_indexes)  [54,230]
                                # eg there are 54 one letters words, 230 2 letters words etc 
                                # remember index starts from 0 hence why even though you are appending the index 
                                # of the word with the new word length, it highlights the number of words of last letter (-1) 

print(len_indexes)
                                  
len_indexes.append(len(wordlist))  #This line runs after the loop ends. It adds the final index — the total number of words — to mark the end of the last group.
                                   # Used becasue the 'loop' would not calcuate the last group  
                                   #There’s no next word after the longest letter words  to trigger another len(wordlist[i]) > length and hence len_indexes.append(i) so the loop never adds the final index.
                                   
print(len_indexes)

# game initalization things 
WIDTH= 1000
HEIGHT= 950

#start image
start_img = pygame.image.load('assets/arts/start.png')
start_img = pygame.transform.scale(start_img, (WIDTH, HEIGHT))

gameover_img = pygame.image.load('assets/arts/gameover.png')
gameover_img = pygame.transform.scale(gameover_img, (600, 350)) 

screen=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Typing Of The Undead")

surface=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
timer=pygame.time.Clock()
fps=60

#game variable 
level=1
num_words=1
active_string=""
score=0
lives=5

paused=True
show_intro=True
submit=""
word_objects=[]
game_over=False
medikits = []

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
           'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
new_level=True

# 2 letter to 8 letters choices as boolean options
choices=[False,True,False,False,False,False,False]

#fonts 
header_font= pygame.font.Font("assets/fonts/ClearSans-Bold.ttf",25)
pause_font =pygame.font.Font("assets/fonts/OldSchoolAdventures-42j9.ttf",30)
banner_font=pygame.font.Font("assets/fonts/MANGOLD.ttf",45)
font= pygame.font.Font("assets/fonts/ClearSans-Bold.ttf",40)

pygame.mixer.init()
intro_music_path = 'assets/sounds/intro.mp3'
main_music_path = 'assets/sounds/music.mp3'
gameover_music_path = 'assets/sounds/game_over.wav'

click=pygame.mixer.Sound("assets/sounds/click.wav")
dead1=pygame.mixer.Sound("assets/sounds/dead1.wav")
dead2=pygame.mixer.Sound("assets/sounds/dead2.wav")
dead3=pygame.mixer.Sound("assets/sounds/dead3.wav")
wrong=pygame.mixer.Sound("assets/sounds/jam.wav")
hurt1=pygame.mixer.Sound("assets/sounds/hurt1.wav")
hurt2=pygame.mixer.Sound("assets/sounds/hurt2.wav")
hurt3=pygame.mixer.Sound("assets/sounds/hurt3.mp3")
attack=pygame.mixer.Sound("assets/sounds/attack.wav")
heal=pygame.mixer.Sound("assets/sounds/heal.wav")

click.set_volume(0.2)
dead1.set_volume(0.1)
dead2.set_volume(0.1)
dead3.set_volume(0.1)
wrong.set_volume(0.3)
heal.set_volume(0.2)

hurt1.set_volume(0.2)
hurt2.set_volume(0.2)
hurt3.set_volume(0.2)
attack.set_volume(0.3)

#high score read in from text file 

file=open("high_score.txt","r")
read=file.readlines()
high_score=int(read[0])
file.close()

def play_music():
    pygame.mixer.music.stop()
    pygame.mixer.music.load(main_music_path)
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)

#load in assests like fonts and sound effect and music

class Word:
    def __init__(self,text,speed,y_pos,x_pos):
        self.text=text
        self.speed=speed 
        self.y_pos=y_pos
        self.x_pos=x_pos
        self.zombie_img = random.choice(zombie_images)  # Randomly select a zombie image
        self.zombie_rect = self.zombie_img.get_rect(topleft=(x_pos - 40, y_pos))  # Position zombie to the left of text

    def draw (self):
        # Draw the zombie image as long as the word exists (it will be removed on submit)
        screen.blit(self.zombie_img, self.zombie_rect)

        color="grey"
        screen.blit(font.render(self.text,True,color),(self.x_pos,self.y_pos))
        act_len=len(active_string)  #Calculates how many characters are in active_string. If active_string = "He", then act_len = 2.
        if active_string==self.text[: act_len]:  #Compares active_string to the beginning of self.text. slices the text from the start up to act_len.  
            screen.blit(font.render(active_string,True,"red"),(self.x_pos,self.y_pos))
         
        # If self.text = "Hello" and active_string = "He", then self.text[:2] = "He", so the condition is True.

    def update(self):
        self.x_pos-=self.speed

        self.zombie_rect.x = self.x_pos - 75  # Update zombie position to stay left of the word
        self.zombie_rect.y = self.y_pos  # Keep y-position aligned with text

class Medikit:
    def __init__(self, text, x_pos, y_pos):
        self.text = text
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.image = medikit_image
        self.rect = self.image.get_rect(topleft=(x_pos, y_pos))

    def draw(self):
        screen.blit(self.image, self.rect)
        screen.blit(font.render(self.text, True, 'white'), (self.x_pos + 60, self.y_pos))
        act_len = len(active_string)
        if active_string == self.text[:act_len]:
            screen.blit(font.render(active_string, True, 'blue'), (self.x_pos + 60, self.y_pos))

class Button:
    def __init__(self,x_pos,y_pos,text,clicked,surf):
        self.x_pos=x_pos
        self.y_pos=y_pos
        self.text=text
        self.clicked=clicked
        self.surf=surf

    def draw(self):
        cir=pygame.draw.circle(self.surf,(46,89,135),(self.x_pos,self.y_pos),35)
        
        if cir.collidepoint(pygame.mouse.get_pos()):
            butts=pygame.mouse.get_pressed()
            if butts[0]:
                pygame.draw.circle(self.surf,(190,35,35),(self.x_pos,self.y_pos),35)
                self.clicked=True
            
            else:
                 pygame.draw.circle(self.surf,(190,89,135),(self.x_pos,self.y_pos),35)

        pygame.draw.circle(self.surf,("white"),(self.x_pos,self.y_pos),35,3)  #white outline
        self.surf.blit(pause_font.render(self.text,True,"white"),(self.x_pos-15,self.y_pos-25))

def draw_screen():
 # screen outlines for background shap and title bar areas
    pygame.draw.rect(screen,("dark grey"),(0,HEIGHT-100,WIDTH,100))  # BLUE RECT AT BOTTOM 
    pygame.draw.rect(screen,("white"),(0,0,WIDTH,HEIGHT,),5) # white border around the screen  5 makes it a border 
    pygame.draw.line(screen,("white"),(250,HEIGHT-100),(250,HEIGHT),2)  # 1ST VERTICAL LINE AT BOTTOM 
    pygame.draw.line(screen,("white"),(700,HEIGHT-100),(700,HEIGHT),2)  # 2ND VERTICAL LINE AT BOTTOM 
    pygame.draw.line(screen,("white"),(0,HEIGHT-100),(WIDTH,HEIGHT-100),2)  # HORIZONTAL LINE 
    pygame.draw.rect(screen,("black"),(0,0,WIDTH,HEIGHT,),2) # black border around the screen  

   # text for showing the current level, player's current input, high score, score, lives 

    screen.blit(header_font.render(f'level:{level}',True,"white"),(10,HEIGHT-75))
    screen.blit(header_font.render(f'"{active_string}"',True,"white"),(270,HEIGHT-75))

    # put pause button here 
    pause_btn=Button(852,HEIGHT-52,"|  |",False,screen)
    pause_btn.draw()

    screen.blit(banner_font.render(f'lives:{lives}',True,"white"),(10,10))
    screen.blit(banner_font.render(f'Ranking: {get_rank(score)}', True, 'white'), (350, 60))
    screen.blit(banner_font.render(f'Score:{score}',True,"white"),(350,10))
    screen.blit(banner_font.render(f'Best:{high_score}',True,"white"),(750,10))
 
    return pause_btn.clicked   # By returning this value, the draw_screen() function communicates user input back to the main game loop.

def draw_pause():
    choice_commits=copy.deepcopy(choices)  # copy of the choices list, changes made to choice_commits inside this function won't affect the original choices list.
    surface=pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)  # create a new surface 
    pygame.draw.rect(surface, (100, 100, 100), (100, 120, 800, 700), 0, 5) #Draw  Background Box 
    pygame.draw.rect(surface,(100,100,100,200),(100,120,800,700),5,5)  #Draw Border Around the Box 200 makes it trasparent
    
    #define buttons for pause menu 
    resume_btn=Button(165,200,">",False,surface)  #create the resume button, False =not clicked 
    resume_btn.draw()  
    quit_btn=Button(732,200,"X",False,surface)
    quit_btn.draw()
     #Inside draw(), the button checks if the mouse is hovering over it and whether the left mouse button (butts[0]) is pressed. 
     # If so, self.clicked = True is set for that button. THe value is returned below eg: return resume_btn.clicked,choice_commits,quit_btn.clicked 
     # and tuple is unpacked at resume_butt,changes,quit_butt=draw_pause() /. Remeber .draw() is a user define function inthe Button Class  

    #define text for pause menu
    surface.blit(header_font.render("MENU",True,"white"),(450,130))
    surface.blit(header_font.render("PLAY",True,"white"),(210,175))
    surface.blit(header_font.render("QUIT",True,"white"),(780,175))
    surface.blit(header_font.render("Active Letter Lengths:",True,"white"),(110,250))

    #define buttons for letter lengths selection

    for i in range(len(choices)):     #Loops through each index in the choices list   len() returns the number of items in a list 
        btn=Button(200+(i*100),350,str(i+2),False,surface)    #Label is i+2  because i starts at 0 and first option is two 
        btn.draw()
        if btn.clicked:                     #  lets the user activate/deactivate specific letter lengths.
            if choice_commits[i]:
                choice_commits[i]=False
            else:
                choice_commits[i]= True 

        if choices[i]:
            pygame.draw.circle(surface,"green",(200+ (i*100),350),35,5)   # highlight it green when clicked =True 

    if game_over:
        surface.blit(gameover_img, (200, 420))

    screen.blit(surface,(0,0))   #Draws the entire pause menu surface onto the main screen.
    return resume_btn.clicked,choice_commits,quit_btn.clicked   # Returns a tuple 

def show_intro_screen():
    pygame.mixer.music.load(intro_music_path)
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)  # Loop indefinitely
    
    screen.blit(start_img, (0, 0))
    screen.blit(font.render('Press any key to start', True, 'white'), (WIDTH/2-190, HEIGHT - 80))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
            if event.type == pygame.MOUSEBUTTONUP:
                    return 'pause'
    return 'start'

def check_answer(scor):
    for wrd in word_objects:
        if wrd.text==submit:
            points= wrd.speed*len(wrd.text)*10*(len(wrd.text)/3)
            scor+=int(points)
            word_objects.remove(wrd)
            random_dead = random.choice([dead1,dead2,dead3])
            random_dead.play()

            #player successful entry sound effect here 
    return scor

def generate_level():
    word_objs=[]  #Initializes an empty list to store the Word objects that will be generated.
    include=[]
    vertical_spacing = (HEIGHT - 150) // level


    if True not in choices:
        choices[0]= True    # Safety check: If no word length is selected, it will select 2 

    for i in range(len(choices)):   #Loops through the choices list. 
        if choices[i]:                  #if true then append corresponding index range
            include.append((len_indexes[i],len_indexes[i+1]))   # creates a tuple between a range for a letter, eg: i=0  Index Range Used len_indexes[0] to len_indexes[1]  which is [54,230] hence all 2 letter words  
    
    if level <= 6:
        num_words = level

    elif level <=12:
        num_words = 6 + (level - 6) // 3     # after level 6 the amount of words increase to 1 words per 3 level

    else:
        num_words = 6 + (level - 6) // 2      # after level 12 the amount of words increase to 1 words per 2 levels 
   
    for i in range(num_words): #Loops once for each word to be generated, based on the current level. Example: If level = 3, it will generate 3 words.
        speed=random.randint(2,3)
# Calculate raw bounds
        raw_start = 10 + (i * vertical_spacing)
        raw_end = (i + 1) * vertical_spacing

        # Clamp both to the allowed range
        clamped_start = max(min(raw_start, HEIGHT - 200), HEIGHT - 800)
        clamped_end = max(min(raw_end, HEIGHT - 200), HEIGHT - 800)

        # Ensure start is not greater than end
        start = min(clamped_start, clamped_end)
        end = max(clamped_start, clamped_end)

        # Final safe random call

        if level>10:     # the existing algorthm clumps up all the words at higher level hence prefer it was just random 
            MIN_Y = 100
            MAX_Y = HEIGHT - 200
            y_pos = random.randint(MIN_Y, MAX_Y)

        else:
            y_pos = random.randint(start, end)
        
        x_pos=random.randint(WIDTH,WIDTH+800)
        ind_sel=random.choice(include)  # Randomly selects one of the index ranges ( A tuple ) 
        index=random.randint(ind_sel[0],ind_sel[1])  # PIcks a random index within the selected range. eg for 2 lettter words : ind_sel[0] 54 ind_sel[1] 230  so it could be 129  
        text=wordlist[index].lower()   #Retrieves the word from wordlist and converts it to lowercase.
        new_word=Word(text,speed,y_pos,x_pos) #Creates a new Word object with the selected attributes.
        word_objs.append(new_word)  
   
    global medikits
    medikits = []
    if lives <= 5:
        for _ in range(random.randint(1, 3)):
            text = random.choice(wordlist).lower()
            x_pos = random.randint(100, WIDTH - 200)
            y_pos = random.randint(200, HEIGHT - 200)
            medikits.append(Medikit(text, x_pos, y_pos))

    return word_objs  #Returns the complete list of generated words to be used in the game.

def check_high_score():
    global high_score
    if score > high_score:
        high_score= score
        file=open("high_score.txt","w")
        file.write(str(int(high_score)))
        file.close()

def get_rank(score):
    if score >= 30000:
        return "Supreme Commander"
    elif score >= 27500:
        return "Field Marshal"
    elif score >= 25000:
        return "General"
    elif score >= 22500:
        return "Colonel"
    elif score >= 20000:
        return "Lieutenant Colonel"
    elif score >= 17500:
        return "Major"
    elif score >= 15000:
        return "Captain"
    elif score >= 12500:
        return "Lieutenant"
    elif score >= 10000:
        return "2nd Lieutenant"
    elif score >= 7500:
        return "Sergeant"  
    elif score >= 5000:
        return "Lance Corporal"  
    elif score >= 3000:
        return "Corporal"
    elif score >= 2000:
        return "Private"
    elif score >= 1000:
        return "Cadet"
    else:
        return "New Recruit"
run=True

while run:

    screen.fill("black")
    timer.tick(fps)

    #draw background screen stuff and statuses and get pause button status 
    pause_butt=draw_screen()   #  it is in a variable  to check if game is pause or not ( False/True )
    
    if show_intro:
        result = show_intro_screen()
        show_intro = False

        play_music()
        
    if new_level and not paused:
        word_objects=generate_level()
        new_level=False

    else:
        for w in word_objects:
            w.draw()
            if not paused:
                w.update()
            if w.x_pos<-200:
                word_objects.remove(w)
                lives-=1 
                attack.play()
                random_hurt = random.choice([hurt1, hurt2,hurt3])
                random_hurt.play()

        for m in medikits:
            m.draw()

        if len(word_objects)<=0 and not paused:
            level+=1
            new_level =True 

        if submit !="":
            init=score   #Saves the current score in a temporary variable init.
            score=check_answer(score)  #Validates the user's input (submit), Updates the score if the answer is correct
            for m in medikits:
                if m.text == submit:
                    lives += 1
                    medikits.remove(m)
                    heal.play()
                    break
            
            submit=""
            if init==score:   #If the score didn't change, the answer was wrong hence play wrong entry sound 
                wrong.play()

    if paused:
        resume_butt,changes,quit_butt=draw_pause()  # You're unpacking that returned tuple into three separate variables  What matters is the order hence changes=choice_commits 
        
        if resume_butt and game_over:
            game_over=False
            paused=False
            score=0
            play_music()

        elif resume_butt:
            paused=False

        if quit_butt:
            check_high_score()
            run=False 
            game=over=False

            #add checking for high score before exiting programme                 
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            check_high_score()   
            run=False
        
        if event.type==pygame.KEYDOWN:
            if not paused:

                if event.unicode.lower() in letters:
                    active_string+=event.unicode.lower()
                    click.play()
                
                if event.key==pygame.K_BACKSPACE and len(active_string) >0:
                    active_string=active_string[:-1]   #slice notation 'Negative Index'  It removes the last character from the string.
                
                
                if event.key==pygame.K_RETURN or event.key== pygame.K_SPACE:
                    submit=active_string
                    active_string=""

            if event.key==pygame.K_ESCAPE :
                if paused and game_over:
                    paused=False
                    game_over=False
                    play_music()
                    score=0

                elif paused:
                    paused=False
                else:
                    paused=True

        if event.type==pygame.MOUSEBUTTONUP and paused:
            if event.button== 1:
                choices=changes

    if pause_butt:   # if pause button is clicked it will pause 
        paused=True

    if lives <=0:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(gameover_music_path)
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)
        game_over=True
        paused=True
        level=1
        lives=5
        word_objects=[]
        new_level=True
        check_high_score()
        medikits = []
        submit = ''
  
    pygame.display.flip()

pygame.quit()
    