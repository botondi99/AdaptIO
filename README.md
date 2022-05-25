# AdaptIO
A következőkben az Adaptív rendszerek modellezése tárgy keretein belül az AdaptIO játékhoz fejlesztett játékos működése lesz bemutatva. <br>
A projektfeladat Giczi Alexandra Laura és Horváth Botond munkája.

## Játék stratégia
A látóteret felosztottuk 9 db, egyenként 13 mezőt tartalmazó részre. Minden egyes rész külön kiértékelésre kerül, és az egyes részeket összevetve dönti el az algoritmus, hogy melyik irányba haladjon tovább a játékos. 


<br>


![kép](https://user-images.githubusercontent.com/82893067/169656005-6dc47363-b6f4-4ae4-9205-2beaf1618d4c.png)

<br>
A látómező egyes részeiben a különböző értékű mezők különböző súlyokkal számítanak bele. Összesen 14 súlyt határoztunk meg az alábbi kritériumok szerint:

* Étel értékei (3)
* Mező távolsága (5)
* Fal
* Kisebb ellenfél
* Nagyobb ellenfél
* Előző mező
* Összefüggő üres mezők száma egy sorban
* Középre tartás
<!-- <br> -->
A súlyok segítségével meghatározható az egyes látómező egységek összértéke. Amelyiknek a legnagyobb az értéke, annak az irányába mozdul a játékos. 9 mozgásirány van, hiszen az x és y irányba is 3 féle (+,-,0) lehetséges értéket kaphat. 
<br>
<br>
Ahhoz, hogy a játékos beragadását egy-egy lépésciklusba megakadályozzuk, vizsgáljuk az előző mezőket amelyeken járt, és ha ismétlődést fedezünk fel, egy random lépéssel kibillentjük ebből a helyzetből. Továbbá az is egy jele lehet a beragadásnak, ha hosszú ideje nem tudott megenni semmit, ezt is számon tartjuk, és a 10. eredménytelen lépés után is véletlenszerű irányba mozdul.

## Súlyok tanítása
A súlyok tanítása genetikus algoritmussal történt. A kezdeti generációban 8 egyedet definiáltunk különböző súlyokkal. Minden egyedre 10 játékot futtattunk 300 tick tartammal, az eredeti 4, illetve egy saját kialakítású pályán, mindegyiken 2 alkalommal. A 10 játék során elért összpontszám adja az egyed fitneszértékét. 
<br>
```python
self.params=[
            [594,16,14,12,10,324,2008,300,1816,2008,10,101,68,1010],
            [18,16,14,12,10,260,280,300,1000,1000,10,5,100,50],
            [18,16,14,12,10,196,280,300,1000,456,10,5,100,98],
            [5,4,3,2,1,200,400,600,500,500,2,5,200,100],
            [180,160,140,120,100,1960,2800,3000,8000,4560,100,50,1000,980],
            [625,125,25,5,1,1000,2000,3000,3000,300,30,100,10,1000],
            [500,400,300,200,100,260,280,300,400,4000,300,20,20,70],
            [150,140,130,120,110,1000,1200,1400,7000,7000,1010,90,1230,900]]
```
<br>
A szelekció során a legjobb 4 egyed kerül kiválasztásra fitneszérték alapján.<br>
A kiválasztott egyedekben a különböző súlyokat 14 biten binárisan ábrázoltuk, majd ebben a formában megtörténhetett a közülük kisorsolt két páron az egypontos keresztezés.
<br>
<br>

![kép](https://user-images.githubusercontent.com/82893067/169661645-2df68e88-6047-4656-bcea-bd3dba9c0936.png)
<br>
A keresztezés után az egyedek egy-egy súlyában 10%-os valószínűséggel mutálódik az egyik bit. <br>
Az így kialakult 4 egyed, illetve az előző generációból szelekcióval kiválasztott 4 egyed alkotja a következő generációt.
Az algoritmust minél tovább futtatjuk, annál hatékonyabb és pontosabb eredményt kapunk. Azt az egyedet, melyet a játékosunknak végül választottunk, fél napos futás után határoztuk meg.

## A játék futtatása saját pályán négy saját játékossal


https://user-images.githubusercontent.com/82893067/169662198-57820a03-9738-4b50-adf6-1bd956c67658.mp4

## Fájlok
A repoba felröltésre került az általunk készített pálya, a bemutatás során előadott prezentáció, illetve a tanuló- és a játékprDependencies


## Dependencies

* numpy
* random
* time
* json
