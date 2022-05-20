#encoding: utf-8

import time
from Client import SocketClient
import json
import random
import numpy as np


# NaiveHunter stratégia implementációja távoli eléréshez.
class RemoteNaiveHunterStrategy:

    def __init__(self):
        # Dinamikus viselkedéshez szükséges változók definíciója
        self.oldpos = None
        self.oldcounter = 0
        self.laststep=[]
        self.score=0
        self.tenscores=0
        self.scores=[]
        self.sizes=[]
        self.games=0
        self.games_before=0
        self.cycle=False
        self.hungry=False
        self.params=[[113,29,9,5,9,488,272,296,1016,812,30,4,106,232]]
        self.path=["E:/adaptivegame/src/maps/01_ring_empty.txt","E:/adaptivegame/src/maps/02_base.txt","E:/adaptivegame/src/maps/03_blockade.txt","E:/adaptivegame/src/maps/04_mirror.txt","E:/adaptivegame/src/maps/05_barricade.txt"]

    # Egyéb függvények...
    def getRandomAction(self):
        actdict = {0: "0", 1: "+", 2: "-"}
        r = np.random.randint(0, 3, 2)
        action = ""
        for act in r:
            action += actdict[act]

        return action

    # Az egyetlen kötelező elem: A játékmestertől jövő információt feldolgozó és választ elküldő függvény
    def processObservation(self, fulljson, sendData):
        """
        :param fulljson: A játékmestertől érkező JSON dict-be konvertálva.
        Két kötelező kulccsal: 'type' (leaderBoard, readyToStart, started, gameData, serverClose) és 'payload' (az üzenet adatrésze).
        'leaderBoard' type a játék végét jelzi, a payload tartalma {'ticks': a játék hossza tickekben, 'players':[{'name': jáétékosnév, 'active': él-e a játékos?, 'maxSize': a legnagyobb elért méret a játék során},...]}
        'readyToStart' type esetén a szerver az indító üzenetre vár esetén, a payload üres (None)
        'started' type esetén a játék elindul, tickLength-enként kiküldés és akciófogadás várható payload {'tickLength': egy tick hossza }
        'gameData' type esetén az üzenet a játékos által elérhető információkat küldi, a payload:
                                    {"pos": abszolút pozíció a térképen, "tick": az aktuális tick sorszáma, "active": a saját életünk állapota,
                                    "size": saját méret,
                                    "leaderBoard": {'ticks': a játék hossza tickekben eddig, 'players':[{'name': jáétékosnév, 'active': él-e a játékos?, 'maxSize': a legnagyobb elért méret a játék során eddig},...]},
                                    "vision": [{"relative_coord": az adott megfigyelt mező relatív koordinátája,
                                                                    "value": az adott megfigyelt mező értéke (0-3,9),
                                                                    "player": None, ha nincs aktív játékos, vagy
                                                                            {name: a mezőn álló játékos neve, size: a mezőn álló játékos mérete}},...] }
        'serverClose' type esetén a játékmester szabályos, vagy hiba okozta bezáródásáról értesülünk, a payload üres (None)
        :param sendData: A kliens adatküldő függvénye, JSON formátumú str bemenetet vár, melyet a játékmester felé továbbít.
        Az elküldött adat struktúrája {"command": Parancs típusa, "name": A küldő azonosítója, "payload": az üzenet adatrésze}
        Elérhető parancsok:
        'SetName' A kliens felregisztrálja a saját nevét a szervernek, enélkül a nevünkhöz tartozó üzenetek nem térnek vissza.
                 Tiltott nevek: a configban megadott játékmester név és az 'all'.
        'SetAction' Ebben az esetben a payload az akció string, amely két karaktert tartalmaz az X és az Y koordináták (matematikai mátrix indexelés) menti elmozdulásra.
                a karakterek értékei '0': helybenmaradás az adott tengely mentén, '+' pozitív irányú lépés, '-' negatív irányú lépés lehet. Amennyiben egy tick ideje alatt
                nem külünk értéket az alapértelmezett '00' kerül végrehajtásra.
        'GameControl' üzeneteket csak a Config.py-ban megadott játékmester névvel lehet küldeni, ezek a játékmenetet befolyásoló üzenetek.
                A payload az üzenet típusát (type), valamint az ahhoz tartozó 'data' adatokat kell, hogy tartalmazza.
                    'start' type elindítja a játékot egy "readyToStart" üzenetet küldött játék esetén, 'data' mezője üres (None)
                    'reset' type egy játék után várakozó 'leaderBoard'-ot küldött játékot állít alaphelyzetbe. A 'data' mező
                            {'mapPath':None, vagy elérési útvonal, 'updateMapPath': None, vagy elérési útvonal} formátumú, ahol None
                            esetén az előző pálya és növekedési map kerül megtartásra, míg elérési útvonal megadása esetén új pálya kerül betöltésre annak megfelelően.
                    'interrupt' type esetén a 'data' mező üres (None), ez megszakítja a szerver futását és szabályosan leállítja azt.
        :return:
        """

        #Változók a modellhez:

        #Távolság figyelembevétele
        d1=self.params[int(((self.games % 80)-(self.games % 10))/10)][0]
        d2=self.params[int(((self.games % 80)-(self.games % 10))/10)][1]
        d3=self.params[int(((self.games % 80)-(self.games % 10))/10)][2]
        d4=self.params[int(((self.games % 80)-(self.games % 10))/10)][3]
        d5=self.params[int(((self.games % 80)-(self.games % 10))/10)][4]

        #Kaja értékei
        f3=self.params[int(((self.games % 80)-(self.games % 10))/10)][5]
        f2=self.params[int(((self.games % 80)-(self.games % 10))/10)][6]
        f1=self.params[int(((self.games % 80)-(self.games % 10))/10)][7]

        #Ellenfelek
        es=self.params[int(((self.games % 80)-(self.games % 10))/10)][8]
        eb=self.params[int(((self.games % 80)-(self.games % 10))/10)][9]

        #fal:
        w=self.params[int(((self.games % 80)-(self.games % 10))/10)][10]

        #Előző mező
        sb=self.params[int(((self.games % 80)-(self.games % 10))/10)][11]

        #Üres mezők egy sorban
        empty=self.params[int(((self.games % 80)-(self.games % 10))/10)][12]

        #Középre tartás
        centering=self.params[int(((self.games % 80)-(self.games % 10))/10)][13]

        # print(self.games)
        
        get_bin = lambda x, n: format(x, 'b').zfill(n)
        
        # Játék rendezéssel kapcsolatos üzenetek lekezelése
        if fulljson["type"] == "leaderBoard":
            print("Game finished after",fulljson["payload"]["ticks"],"ticks!")
            print("Leaderboard:")
            for score in fulljson["payload"]["players"]:
                print(score["name"],score["active"], score["maxSize"])

            time.sleep(0.1)
            sendData(json.dumps({"command": "GameControl", "name": "master",
                                 "payload": {"type": "reset", "data": {"mapPath": None, "updateMapPath": None}}}))
            self.games=self.games+1
            print("GAMES")
            print(self.games)

        if fulljson["type"] == "readyToStart":
            print("Game is ready, starting in 5")
            time.sleep(0.5)
            sendData(json.dumps({"command": "GameControl", "name": "master",
                                 "payload": {"type": "start", "data": None}}))

        if fulljson["type"] == "started":
            print("Startup message from server.")
            print("Ticks interval is:",fulljson["payload"]["tickLength"])


        # Akció előállítása bemenetek alapján (egyezik a NaiveHunterBot-okéval)
        elif fulljson["type"] == "gameData":
            jsonData = fulljson["payload"]
            if "pos" in jsonData.keys() and "tick" in jsonData.keys() and "active" in jsonData.keys() and "size" in jsonData.keys() and "vision" in jsonData.keys():
                if self.oldpos is not None:
                    if tuple(self.oldpos) == tuple(jsonData["pos"]):
                        self.oldcounter += 1
                    else:
                        self.oldcounter = 0
                if jsonData["active"]:
                    self.oldpos = jsonData["pos"].copy()

                vals = []
                sum1=0
                sum2=0
                sum3=0
                sum4=0
                sum5=0
                sum6=0
                sum7=0
                sum8=0
                sum9=0

                for index in range(0, 81):
                    field=jsonData["vision"][index]
                    field_value=0
                    if field["player"] is not None:
                        if tuple(field["relative_coord"]) == (0, 0):
                            if field["value"] == 1:
                                field_value=f1
                            elif field["value"] == 2:
                                field_value=f2
                            elif field["value"] == 3:
                                field_value=f3
                            elif field["value"] == 9:
                                field_value=-w
                            else:
                                field_value=0
                        elif field["player"]["size"] * 1.1 < jsonData["size"]:
                            field_value=es*(field["player"]["size"])
                        else:
                            field_value=-eb
                    else:
                        if field["value"] == 1:
                            field_value=f1
                        elif field["value"] == 2:
                            field_value=f2
                        elif field["value"] == 3:
                            field_value=f3
                        elif field["value"] == 9:
                            field_value=-w
                            if field["relative_coord"][0] == 1 and field["relative_coord"][1] == 1 :
                                vals.append(1)
                            if field["relative_coord"][0] == 1 and field["relative_coord"][1] == 0 :
                                vals.append(2)
                            if field["relative_coord"][0] == 1 and field["relative_coord"][1] == -1 :
                                vals.append(3)
                            if field["relative_coord"][0] == 0 and field["relative_coord"][1] == -1 :
                                vals.append(4)
                            if field["relative_coord"][0] == -1 and field["relative_coord"][1] == -1 :
                                vals.append(5)
                            if field["relative_coord"][0] == -1 and field["relative_coord"][1] == 0 :
                                vals.append(6)
                            if field["relative_coord"][0] == -1 and field["relative_coord"][1] == 1 :
                                vals.append(7)
                            if field["relative_coord"][0] == 0 and field["relative_coord"][1] == 1 :
                                vals.append(8)
                        else:
                            field_value=0
                    if abs(field["relative_coord"][0]) > abs(field["relative_coord"][1]):
                        distance=abs(field["relative_coord"][0])
                    else:
                        distance=abs(field["relative_coord"][1])
                    # print("distance: ")
                    # print(distance)
                    if distance==1:
                        field_value=field_value*d1
                    if distance==2:
                        field_value=field_value*d2
                    if distance==3:
                        field_value=field_value*d3
                    if distance==4:
                        field_value=field_value*d4
                    if distance==5:
                        field_value=field_value*d5

                    if index==0 or index==3 or index==4 or index==5 or index==11 or index==12 or index==13 or index==20 or index==21 or index==22 or index==29 or index==30 or index==31:
                        sum1=sum1+field_value
                    if index==6 or index==7 or index==13 or index==14 or index==15 or index==16 or index==22 or index==23 or index==24 or index==25 or index==31 or index==32 or index==33:
                        sum2=sum2+field_value
                    if index==31 or index==32 or index==33 or index==34 or index==41 or index==42 or index==43 or index==44 or index==45 or index==51 or index==52 or index==53 or index==54:
                        sum3=sum3+field_value
                    if index==51 or index==52 or index==53 or index==60 or index==61 or index==62 or index==63 or index==69 or index==70 or index==71 or index==72 or index==78 or index==79:
                        sum4=sum4+field_value
                    if index==49 or index==50 or index==51 or index==58 or index==59 or index==60 or index==67 or index==68 or index==69 or index==75 or index==76 or index==77 or index==80:
                        sum5=sum5+field_value
                    if index==47 or index==48 or index==49 or index==55 or index==56 or index==57 or index==58 or index==64 or index==65 or index==66 or index==67 or index==73 or index==74:
                        sum6=sum6+field_value
                    if index==26 or index==27 or index==28 or index==29 or index==35 or index==36 or index==37 or index==38 or index==39 or index==46 or index==47 or index==48 or index==49:
                        sum7=sum7+field_value
                    if index==1 or index==2 or index==8 or index==9 or index==10 or index==11 or index==17 or index==18 or index==19 or index==20 or index==27 or index==28 or index==29:
                        sum8=sum8+field_value
                    if index==21 or index==29 or index==30 or index==31 or index==38 or index==39 or index==40 or index==41 or index==42 or index==49 or index==50 or index==51 or index==59:
                        sum9=sum9+field_value 

                empty_up_last=1
                empty_up=0
                for index in range(41, 46):
                    field=jsonData["vision"][index]
                    if field["value"] != 9:
                        empty_up=empty_up+empty_up_last
                    else:
                        empty_up_last=0

                empty_right=0
                if jsonData["vision"][50]["value"]!= 9 and jsonData["vision"][59]["value"]!= 9 and jsonData["vision"][68]["value"]!= 9 and jsonData["vision"][76]["value"]!= 9 and jsonData["vision"][80]["value"]!= 9:
                    empty_right=5
                elif jsonData["vision"][50]["value"]!= 9 and jsonData["vision"][59]["value"]!= 9 and jsonData["vision"][68]["value"]!= 9 and jsonData["vision"][76]["value"]!= 9:
                    empty_right=4
                elif jsonData["vision"][50]["value"]!= 9 and jsonData["vision"][59]["value"]!= 9 and jsonData["vision"][68]["value"]!= 9:
                    empty_right=3
                elif jsonData["vision"][50]["value"]!= 9 and jsonData["vision"][59]["value"]!= 9:
                    empty_right=2
                elif jsonData["vision"][50]["value"]!= 9:
                    empty_right=1
                else: 
                    empty_right=0

                empty_down=0
                if jsonData["vision"][40]["value"]!= 9 and jsonData["vision"][39]["value"]!= 9 and jsonData["vision"][38]["value"]!= 9 and jsonData["vision"][37]["value"]!= 9 and jsonData["vision"][36]["value"]!= 9:
                    empty_down=5
                elif jsonData["vision"][40]["value"]!= 9 and jsonData["vision"][39]["value"]!= 9 and jsonData["vision"][38]["value"]!= 9 and jsonData["vision"][37]["value"]!= 9:
                    empty_down=4
                elif jsonData["vision"][40]["value"]!= 9 and jsonData["vision"][39]["value"]!= 9 and jsonData["vision"][38]["value"]!= 9:
                    empty_down=3
                elif jsonData["vision"][40]["value"]!= 9 and jsonData["vision"][39]["value"]!= 9:
                    empty_down=2
                elif jsonData["vision"][40]["value"]!= 9:
                    empty_down=1
                else:
                    empty_down=0


                empty_left=0
                if jsonData["vision"][30]["value"]!= 9 and jsonData["vision"][21]["value"]!= 9 and jsonData["vision"][12]["value"]!= 9 and jsonData["vision"][4]["value"]!= 9 and jsonData["vision"][0]["value"]!= 9:
                    empty_left=5
                elif jsonData["vision"][30]["value"]!= 9 and jsonData["vision"][21]["value"]!= 9 and jsonData["vision"][12]["value"]!= 9 and jsonData["vision"][4]["value"]!= 9:
                    empty_left=4
                elif jsonData["vision"][30]["value"]!= 9 and jsonData["vision"][21]["value"]!= 9 and jsonData["vision"][12]["value"]!= 9:
                    empty_left=3
                elif jsonData["vision"][30]["value"]!= 9 and jsonData["vision"][21]["value"]!= 9:
                    empty_left=2
                elif jsonData["vision"][30]["value"]!= 9:
                    empty_left=1
                else:
                    empty_left=0


                empty_topleft=0
                if jsonData["vision"][31]["value"]!= 9 and jsonData["vision"][23]["value"]!= 9 and jsonData["vision"][15]["value"]!= 9:
                    empty_topleft=5
                elif jsonData["vision"][31]["value"]!= 9 and jsonData["vision"][23]["value"]!= 9:
                    empty_topleft=3
                elif jsonData["vision"][31]["value"]!= 9:
                    empty_topleft=1
                
                empty_topright=0
                if jsonData["vision"][51]["value"]!= 9 and jsonData["vision"][61]["value"]!= 9 and jsonData["vision"][71]["value"]!= 9:
                    empty_topright=5
                elif jsonData["vision"][51]["value"]!= 9 and jsonData["vision"][62]["value"]!= 9:
                    empty_topright=3
                elif jsonData["vision"][51]["value"]!= 9:
                    empty_topright=1

                empty_bottomright=0
                if jsonData["vision"][49]["value"]!= 9 and jsonData["vision"][57]["value"]!= 9 and jsonData["vision"][65]["value"]!= 9:
                    empty_bottomright=5
                elif jsonData["vision"][49]["value"]!= 9 and jsonData["vision"][57]["value"]!= 9:
                    empty_bottomright=3
                elif jsonData["vision"][49]["value"]!= 9:
                    empty_bottomright=1

                empty_bottomleft=0
                if jsonData["vision"][29]["value"]!= 9 and jsonData["vision"][19]["value"]!= 9 and jsonData["vision"][9]["value"]!= 9:
                    empty_bottomleft=5
                elif jsonData["vision"][29]["value"]!= 9 and jsonData["vision"][19]["value"]!= 9:
                    empty_bottomleft=3
                elif jsonData["vision"][29]["value"]!= 9:
                    empty_bottomleft=1

                sum1=sum1+empty*empty_left
                sum3=sum3+empty*empty_up
                sum5=sum5+empty*empty_right
                sum7=sum7+empty*empty_down
                sum4=sum4+empty*empty_topright
                sum2=sum2+empty*empty_topleft
                sum6=sum6+empty*empty_bottomright
                sum8=sum8+empty*empty_bottomleft


                forbidden=-100000
                waitrand=np.random.randint(0, 1)
                if waitrand==0:
                    sum9=-10000
                #print(vals)
                for i in vals:
                    if i==1:
                        sum4=forbidden
                    if i==2:
                        sum5=forbidden
                    if i==3:
                        sum6=forbidden
                    if i==4:
                        sum7=forbidden
                    if i==5:
                        sum8=forbidden
                    if i==6:
                        sum1=forbidden
                    if i==7:
                        sum2=forbidden
                    if i==8:
                        sum3=forbidden

                if len(self.laststep)>1:
                    before=len(self.laststep)-1
                    step_before=self.laststep[before]
                    if step_before=="++":
                        if sum8<0:
                            sum8=sum8*sb
                        else:
                            sum8=sum8/sb
                    elif step_before=="+0":
                        if sum1<0:
                            sum1=sum1*sb
                        else:
                            sum1=sum1/sb
                    elif step_before=="+-":
                        if sum2<0:
                            sum2=sum2*sb
                        else:
                            sum2=sum2/sb
                    elif step_before=="0-":
                        if sum3<0:
                            sum3=sum3*sb
                        else:
                            sum3=sum3/sb
                    elif step_before=="--":
                        if sum4<0:
                            sum4=sum4*sb
                        else:
                            sum4=sum4/sb
                    elif step_before=="-0":
                        if sum5<0:
                            sum5=sum5*sb
                        else:
                            sum5=sum5/sb
                    elif step_before=="+-":
                        if sum6<0:
                            sum6=sum6*sb
                        else:
                            sum6=sum6/sb
                    elif step_before=="+-":
                        if sum7<0:
                            sum7=sum7*sb
                        else:
                            sum7=sum7/sb

                if jsonData['pos'][0]-19 > 0:
                    sum1=sum1+centering
                    sum2=sum2+centering
                    sum8=sum8+centering
                else:
                    sum4=sum4+centering
                    sum5=sum5+centering
                    sum6=sum6+centering

                if jsonData['pos'][1]-19 > 0:
                    sum4=sum4+centering
                    sum2=sum2+centering
                    sum3=sum3+centering
                else:
                    sum6=sum6+centering
                    sum7=sum7+centering
                    sum8=sum8+centering

                maxvalue=max(sum1, sum2, sum3, sum4, sum5, sum6, sum7, sum8, sum9)

                maxcounter=0
                strings=[]
  
                if sum4==maxvalue:
                    strings.append("++")
                    maxcounter=maxcounter+1
                if sum5==maxvalue:
                    strings.append("+0")
                    maxcounter=maxcounter+1
                if sum6==maxvalue:
                    strings.append("+-")
                    maxcounter=maxcounter+1
                if sum7==maxvalue:
                    strings.append("0-")
                    maxcounter=maxcounter+1
                if sum8==maxvalue:
                    strings.append("--")
                    maxcounter=maxcounter+1
                if sum1==maxvalue:
                    strings.append("-0")
                    maxcounter=maxcounter+1
                if sum2==maxvalue:
                    strings.append("-+")
                    maxcounter=maxcounter+1
                if sum3==maxvalue:
                    strings.append("0+")
                    maxcounter=maxcounter+1
                if sum9==maxvalue:
                    strings.append("00")
                    maxcounter=maxcounter+1
                if maxcounter > 1:
                    randnumber=np.random.randint(0, maxcounter-1)
                    actstring=strings[randnumber]
                else:
                    actstring=strings[0]

                for i in range(2,10):
                    if len(self.laststep)>i*2:
                        if self.laststep[len(self.laststep)-i:len(self.laststep)] == self.laststep[len(self.laststep)-2*i:len(self.laststep)-i]:
                            self.cycle=True

                if len(self.sizes)>10:
                    if self.sizes[len(self.sizes)-1] == self.sizes[len(self.sizes)-2] == self.sizes[len(self.sizes)-3] == self.sizes[len(self.sizes)-4] == self.sizes[len(self.sizes)-5] == self.sizes[len(self.sizes)-6] == self.sizes[len(self.sizes)-7] == self.sizes[len(self.sizes)-8] == self.sizes[len(self.sizes)-9]:
                        self.hungry=True
                    
                
                if(self.cycle or self.hungry):
                    actdict = {0: "0", 1: "+", 2: "-"}
                    r = np.random.randint(0, 3, 2)
                    action = ""
                    for act in r:
                        action += actdict[act]
                    actstring=action
                    self.cycle=False
                    self.hungry=False
                    self.sizes[len(self.sizes)-1]=self.sizes[len(self.sizes)-1]*(-1)

                self.laststep.append(actstring)
                # print(self.laststep)
                before=len(self.laststep)-2
                # print(self.laststep[before])
                self.sizes.append(jsonData['size'])
                self.score=jsonData['size']

                # Akció JSON előállítása és elküldése
                sendData(json.dumps({"command": "SetAction", "name": "Brown", "payload": actstring}))



if __name__=="__main__":
    # Példányosított stratégia objektum
    hunter = RemoteNaiveHunterStrategy()

    # Socket kliens, melynek a szerver címét kell megadni (IP, port), illetve a callback függvényt, melynek szignatúrája a fenti
    # callback(fulljson, sendData)
    client = SocketClient("10.0.0.113", 42069, hunter.processObservation)

    # Kliens indítása
    client.start()
    # Kis szünet, hogy a kapcsolat felépülhessen, a start nem blockol, a kliens külső szálon fut
    time.sleep(0.1)
    # Regisztráció a megfelelő névvel
    client.sendData(json.dumps({"command": "SetName", "name": "Brown", "payload": None}))

    # Nincs blokkoló hívás, a főszál várakozó állapotba kerül, itt végrehajthatók egyéb műveletek a kliens automata működésétől függetlenül.