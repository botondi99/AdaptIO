# AdaptIO
A következőkben az Adaptív rendszerek modellezése tárgy keretein belül az AdaptIO játékhoz fejlesztett játékos működése lesz bemutatva. <br>
A projektfeladat Giczi Alexandra Laura és Horváth Botond munkája.

## Játék stratégia
A látóteret felosztottuk 9 db, egyenként 13 mezőt tartalmazó részre. Minden egyes rész külön kiértékelésre kerül, és az egyes részeket összevetve dönti el az algoritmus, hogy melyik irányba haladjon tovább a játékos. 
<br>
![kép](https://user-images.githubusercontent.com/82893067/169656005-6dc47363-b6f4-4ae4-9205-2beaf1618d4c.png)

<br>
A látómező egyes részeiben a különböző értékű mezők különböző súlyokkal számítanak bele. Összesen 14 súlyt határoztunk meg az alábbi kritériumok szerint:<br>
⋅⋅* Étel értékei (3)
* Mező távolsága (5)
*Fal
*Kisebb ellenfél
*Nagyobb ellenfél
*Előző mező
*Összefüggő üres mezők száma egy sorban
*Középre tartás



## A játék futtatása saját pályán négy saját játékossal
https://user-images.githubusercontent.com/82893067/169651100-b72ddf17-a91f-4502-ae96-a99c752b6baa.mp4

