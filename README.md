<h1 align ="center"> Echoes from Alexandria: A Large Resource for Multilingual Book Summarization </h1>
<p>
<a href="">
        <img alt="Python" src="https://img.shields.io/badge/Python 3.8--3.9-blue?style=for-the-badge&logo=python&logoColor=white">
    </a>
    <a href="https://black.readthedocs.io/en/stable/">
        <img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-black.svg?style=for-the-badge&labelColor=gray">
    </a>
        
</p>

This repository contains the code of [Echoes from Alexandria: a Large Resource for Multilingual Book Summarization](https://aclanthology.org/2023.findings-acl.54/). 
This work was accepted at ACL 2023.
If you find our paper, code or framework useful, please reference this work in your paper:

```
@inproceedings{scire-etal-2023-echoes,
    title = "Echoes from Alexandria: A Large Resource for Multilingual Book Summarization",
    author = "Scir{\`e}, Alessandro  and
      Conia, Simone  and
      Ciciliano, Simone  and
      Navigli, Roberto",
    booktitle = "Findings of the Association for Computational Linguistics: ACL 2023",
    month = jul,
    year = "2023",
    address = "Toronto, Canada",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2023.findings-acl.54",
    pages = "853--867"
}
```

## Setup the environment

Requirements:
* Debian-based (e.g. Debian, Ubuntu, ...) system 
* [conda](https://docs.conda.io/en/latest/) installed

After having installed conda, use this command to create a new environment:
```
conda create -n echoes-from-alexandria python=3.8
```
Then, activate the newly-created environment and install the required libraries:
```
conda activate echoes-from-alexandria
pip install -r requirements.txt
```
Download and unzip the required data from:
[https://drive.google.com/drive/folders/1Ve5EhafQO2C1RAMiJkpJ7h2PhvlVJrWq?usp=sharing
](https://drive.google.com/drive/folders/1Ve5EhafQO2C1RAMiJkpJ7h2PhvlVJrWq?usp=sharing)

put the unzipped files and folders inside _data_.

## Generate Echoes

In order to generate the Echo-Wiki and Echo-XSum datasets, run the following script:
```
PYTHONPATH=. python dataset_generation/src/main/generate_echoes.py 
```
The execution of this script may take a while, since it will download the required Wikisource and Gutenberg
dumps.

You can configure the dumps destination folder by editing the variable BASE_PATH in dataset_generation/src/utils/constants.py,
and the Wikisource dump date by changing the variable WIKISOURCE_DUMP_DATE in the same file.
If you decide to change the BASE_PATH variable, please remember to move the 'wikipedia-dump' folder to the new path you specified.

The output folder, namely 'echoes_from_alexandria', will be organized as follows:
```
echoes_from_alexandria
├── books
│   ├── en_Macbeth_macbeth.jsonl
│   ├── ...
│   └── ...
├── echo-wiki.jsonl
└── echo-xsum.jsonl
```

The 'books' folder contains all the book texts, one json per book, in the following format:
```
{
    "title": "macbeth",
    "wikipedia_page": "Macbeth",
    "language": "en", 
    "source": "gutenberg",
    "text": "the book text ..."
}
```

The echo-wiki.jsonl and echo-xsum.jsonl files are structured in the following way:
```
{
   "title":{
      "en":"Macbeth",
      "de":"Macbeth",
      "es":"Macbeth",
      "fr":"Macbeth",
      "it":"Macbeth"
   },
   "sections":{
      "en":[
         "plot"
      ],
      "de":[
         "handlung"
      ],
      "es":[
         "sinopsis"
      ],
      "it":[
         "trama"
      ]
   },
   "versions":[
      {
         "title":"macbeth",
         "language":"en",
         "filepath":"echoes_from_alexandria/books/en_Macbeth_macbeth.jsonl"
      },
      {
         "title":"Shakespeare - First Folio facsimile (1910)",
         "language":"en",
         "filepath":"echoes_from_alexandria/books/en_Macbeth_Shakespeare - First Folio facsimile (1910).jsonl"
      },
      {
         "title":"macbeth",
         "language":"de",
         "filepath":"echoes_from_alexandria/books/de_Macbeth_macbeth.jsonl"
      },
      {
         "title":"macbeth",
         "language":"fr",
         "filepath":"echoes_from_alexandria/books/fr_Macbeth_macbeth.jsonl"
      },
      {
         "title":"Macbeth (Men\u00e9ndez y Pelayo tr.)",
         "language":"es",
         "filepath":"echoes_from_alexandria/books/es_Macbeth_Macbeth (Men\u00e9ndez y Pelayo tr.).jsonl"
      },
      {
         "title":"Macbeth (fragmento)",
         "language":"es",
         "filepath":"echoes_from_alexandria/books/es_Macbeth_Macbeth (fragmento).jsonl"
      }
   ],
   "summaries":{
      "en":[
         "Act I\n\nAmid thunder and lightning, Three Witches decide that their next meeting will be with Macbeth. In the following scene, a wounded sergeant reports to King Duncan of Scotland that his generals Banquo and Macbeth, the Thane of Glamis,  have just defeated the allied forces of Norway and Ireland, who were led by the traitorous Macdonwald, the Thane of Cawdor. Macbeth, the King's kinsman, is praised for his bravery and fighting prowess.\n\nIn the following scene, Macbeth and Banquo discuss the weather and their victory. As they wander onto a heath, the Three Witches enter and greet them with prophecies. Though Banquo challenges them first, they address Macbeth, hailing him as \"Thane of Glamis,\" \"Thane of Cawdor,\" and that he will \"be King hereafter\". Macbeth appears to be stunned to silence. When Banquo asks of his own fortunes, the witches respond paradoxically, saying that he will be less than Macbeth, yet happier, and less successful, yet more. He will father a line of kings, though he himself will not be one. While the two men wonder at these pronouncements, the witches vanish, and another thane, Ross, arrives and informs Macbeth of his newly bestowed title: Thane of Cawdor. The first prophecy is thus fulfilled, and Macbeth, previously sceptical, immediately begins to harbour ambitions of becoming king.\n\nKing Duncan welcomes and praises Macbeth and Banquo, and Duncan declares that he will spend the night at Macbeth's castle at Inverness; Duncan also names his son Malcolm as his heir. Macbeth sends a message ahead to his wife, Lady Macbeth, telling her about the witches' prophecies. Lady Macbeth suffers none of her husband's uncertainty and wishes him to murder Duncan in order to obtain kingship. When Macbeth arrives at Inverness, she overrides all of her husband's objections by challenging his manhood and successfully persuades him to kill the king that very night. He and Lady Macbeth plan to get Duncan's two chamberlains drunk so that they will black out; the next morning they will blame the chamberlains for the murder. Since the chamberlains would remember nothing whatsoever, they would be blamed for the deed.\n\nAct II\n\nWhile Duncan is asleep, Macbeth stabs him, despite his doubts and a number of supernatural portents, including a hallucination of a bloody dagger. He is so shaken that Lady Macbeth has to take charge. In accordance with her plan, she frames Duncan's sleeping servants for the murder by placing bloody daggers on them. Early the next morning, Lennox, a Scottish nobleman, and Macduff, the loyal Thane of Fife, arrive. A porter opens the gate and Macbeth leads them to the king's chamber, where Macduff discovers Duncan's body. Macbeth murders the guards to prevent them from professing their innocence, but claims he did so in a fit of anger over their misdeeds. Duncan's sons Malcolm and Donalbain flee to England and Ireland, respectively, fearing that whoever killed Duncan desires their demise as well. The rightful heirs' flight makes them suspects and Macbeth assumes the throne as the new King of Scotland as a kinsman of the dead king. Banquo reveals this to the audience, and while sceptical of the new King Macbeth, he remembers the witches' prophecy about how his own descendants would inherit the throne; this makes him suspicious of Macbeth.\n\nAct III\n\nDespite his success, Macbeth, also aware of this part of the prophecy, remains uneasy. Macbeth invites Banquo to a royal banquet, where he discovers that Banquo and his young son, Fleance, will be riding out that night. Fearing Banquo's suspicions, Macbeth arranges to have him murdered, by hiring two men to kill them, later sending a Third Murderer, presumably to ensure that the deed is completed. The assassins succeed in killing Banquo, but Fleance escapes. Macbeth becomes furious: he fears that his power remains insecure as long as an heir of Banquo remains alive.\n\nAt the banquet, Macbeth invites his lords and Lady Macbeth to a night of drinking and merriment. Banquo's ghost enters and sits in Macbeth's place. Macbeth raves fearfully, startling his guests, as the ghost is visible only to him. The others panic at the sight of Macbeth raging at an empty chair, until a desperate Lady Macbeth tells them that her husband is merely afflicted with a familiar and harmless malady. The ghost departs and returns once more, causing the same riotous anger and fear in Macbeth. This time, Lady Macbeth tells the visitors to leave, and they do so. At the end Hecate scolds the three weird sisters for helping Macbeth, especially without consulting her. Hecate Instructs the Witches to give Macbeth false security. Note that some scholars believe the Hecate scene was added in later. \n\nMacbeth consulting the Vision of the Armed Head by Johann Heinrich F\u00fcssli\n\nAct IV\n\nMacbeth, disturbed, visits the three witches once more and asks them to reveal the truth of their prophecies to him. To answer his questions, they summon horrible apparitions, each of which offers predictions and further prophecies to put Macbeth's fears at rest. First, they conjure an armoured head, which tells him to beware of Macduff (IV.i.72). Second, a bloody child tells him that no one born of a woman will be able to harm him. Thirdly, a crowned child holding a tree states that Macbeth will be safe until Great Birnam Wood comes to Dunsinane Hill. Macbeth is relieved and feels secure because he knows that all men are born of women and forests cannot possibly move.\n\nMacbeth also asks whether Banquo's sons will ever reign in Scotland, to which the witches conjure a procession of eight crowned kings, all similar in appearance to Banquo, and the last carrying a mirror that reflects even more kings. Macbeth realises that these are all Banquo's descendants having acquired kingship in numerous countries.\n\nAfter the witches perform a mad dance and leave, Lennox enters and tells Macbeth that Macduff has fled to England. Macbeth orders Macduff's castle be seized, and, most cruelly, sends murderers to slaughter Macduff, as well as Macduff's wife and children. Although Macduff is no longer in the castle, everyone in Macduff's castle is put to death, including Lady Macduff and their young son.\n\nLady Macbeth sleepwalking by Johann Heinrich F\u00fcssli\n\nAct V\n\nLady Macbeth becomes racked with guilt from the crimes she and her husband have committed. At night, in the king's palace at Dunsinane, a doctor and a gentlewoman discuss Lady Macbeth's strange habit of sleepwalking. Suddenly, Lady Macbeth enters in a trance with a candle in her hand. Bemoaning the murders of Duncan, Lady Macduff, and Banquo, she tries to wash off imaginary bloodstains from her hands, all the while speaking of the terrible things she knows she pressed her husband to do. She leaves, and the doctor and gentlewoman marvel at her descent into madness.\n\nIn England, Macduff is informed by Ross that his \"castle is surprised; wife and babes / Savagely slaughter'd\" (IV.iii.204\u2013205). When this news of his family's execution reaches him, Macduff is stricken with grief and vows revenge. Prince Malcolm, Duncan's son, has succeeded in raising an army in England, and Macduff joins him as he rides to Scotland to challenge Macbeth's forces. The invasion has the support of the Scottish nobles, who are appalled and frightened by Macbeth's tyrannical and murderous behaviour. Malcolm leads an army, along with Macduff and Englishmen Siward (the Elder), the Earl of Northumberland, against Dunsinane Castle. While encamped in Birnam Wood, the soldiers are ordered to cut down and carry tree branches to camouflage their numbers.\n\nBefore Macbeth's opponents arrive, he receives news that Lady Macbeth has killed herself, causing him to sink into a deep and pessimistic despair and deliver his \"To-morrow, and to-morrow, and to-morrow\" soliloquy (V.v.17\u201328). Though he reflects on the brevity and meaninglessness of life, he nevertheless awaits the English and fortifies Dunsinane. He is certain that the witches' prophecies guarantee his invincibility, but is struck with fear when he learns that the English army is advancing on Dunsinane shielded with boughs cut from Birnam Wood, in apparent fulfillment of one of the prophecies.\n\nA battle culminates in Macduff's confrontation with Macbeth, who kills Young Siward in combat. The English forces overwhelm his army and castle. Macbeth boasts that he has no reason to fear Macduff, for he cannot be killed by any man born of woman. Macduff declares that he was \"from his mother's womb / Untimely ripp'd\" (V.8.15\u201316), (i.e., born by Caesarean section and not a natural birth) and is not \"of woman born\", fulfilling the second prophecy. Macbeth realises too late that he has misinterpreted the witches' words. Though he realises that he is doomed, and despite Macduff urging him to yield, he is unwilling to surrender and continues fighting. Macduff kills and beheads him, thus fulfilling the remaining prophecy.\n\nMacduff carries Macbeth's head onstage and Malcolm discusses how order has been restored. His last reference to Lady Macbeth, however, reveals tis thought, by self and violent hands / Took off her life\" (V.ix.71\u201372), but the method of her suicide is undisclosed. Malcolm, now the King of Scotland, declares his benevolent intentions for the country and invites all to see him crowned at Scone.\n\n(Although Malcolm, and not Fleance, is placed on the throne, the witches' prophecy concerning Banquo (\"Thou shalt get kings\") was known to the audience of Shakespeare's time to be true: James VI of Scotland (later also James I of England) was supposedly a descendant of Banquo.)"
      ],
      "de":[
         " Akt I \nIm 1. Akt werden die zentralen Figuren sowie Setting und Thema vorgestellt (Exposition): Macbeth bekommt von den drei Hexen seinen Aufstieg zum K\u00f6nig prophezeit.\n\nDas Drama beginnt mit dem gespenstischen Auftritt von drei Hexen, die inmitten eines Gewitters dar\u00fcber beraten, wann und wo sie wieder zusammentreffen wollen. Gleichzeitig findet bei Forres die letzte Schlacht der k\u00f6niglichen Truppen Duncans gegen den norwegischen K\u00f6nig Sweno statt, der vom Rebellen Macdonwald unterst\u00fctzt wird. Im Feldlager nahe dem Schlachtfeld wird K\u00f6nig Duncan dar\u00fcber unterrichtet, dass Macdonwald von Macbeth besiegt wurde und auch der Thane of Cawdor die Norweger unterst\u00fctzt hat. Nach dem Sieg der Schotten ordnet Duncan an, Amt und W\u00fcrden des verr\u00e4terischen Thane of Cawdor auf Macbeth zu \u00fcbertragen.\n\nZusammen mit Banquo trifft Macbeth auf seinem R\u00fcckweg von der Schlacht in einer Heide auf die Hexen. Diese sprechen ihn als Thane of Cawdor an und prophezeien ihm, bald K\u00f6nig zu sein; seinem Begleiter Banquo hingegen verk\u00fcnden sie, dereinst Ahnvater von K\u00f6nigen zu sein. Macbeth, in Unkenntnis der letzten milit\u00e4rischen Ereignisse, ist von dieser Weissagung mehr verwirrt als \u00fcberzeugt. Als ihn jedoch kurz darauf Rosse \u00fcber die Entscheidung des K\u00f6nigs, seine Ernennung zum Thane of Cawdor, in Kenntnis setzt und sich der erste Teil der Prophezeiung dadurch schnell erf\u00fcllt, kommt er ins Gr\u00fcbeln und freundet sich insgeheim bereits mit dem Gedanken an, den alten K\u00f6nig Duncan abzul\u00f6sen.\n\nVon ihrem Gemahl \u00fcber die seltsame Begegnung mit den Hexen informiert, dr\u00e4ngt die ehrgeizige Lady Macbeth ihren Mann zum Handeln: Da sie die M\u00f6glichkeit ausschlie\u00dft, dass ihr Mann den Thron auf nat\u00fcrlichem Wege besteigen kann, fasst sie kurzerhand den Mord an K\u00f6nig Duncan ins Auge. Macbeth schreckt zun\u00e4chst davor zur\u00fcck, gibt aber, um vor seiner Frau nicht als Feigling dazustehen und seine von ihr infrage gestellte M\u00e4nnlichkeit zu beweisen, schlie\u00dflich nach und willigt ein, Duncan bei dessen unmittelbar bevorstehendem Besuch auf Macbeths Burg in Inverness zu t\u00f6ten. Die Eheleute beginnen mit den Vorbereitungen ihrer Untat, w\u00e4hrend Duncan mit seinen S\u00f6hnen sowie die Thanes und deren Gefolge als G\u00e4ste in Inverness eintreffen.\n\n Akt II \nDer 2. Akt schildert die steigende Handlung: Macbeth ermordet Duncan und ernennt sich selbst zum neuen K\u00f6nig. Bis hierhin handelt er aber nicht nur aus Eigenantrieb, sondern l\u00e4sst sich von seiner Frau zur Tat anstacheln, die seine Bedenken zerstreut.\n\nAls sich Banquo und sein Sohn Fleance zur Nachtruhe auf ihr Zimmer begeben wollen, sto\u00dfen sie im stockdunklen Burghof auf Macbeth.\nBanquo gesteht, dass ihn die Weissagungen der Hexen noch im Traum verfolgt haben. Macbeth dagegen behauptet, nicht mehr daran zu denken, erkl\u00e4rt sich jedoch bereit, das Thema zu einem sp\u00e4teren Zeitpunkt noch einmal mit Banquo zu besprechen. Nachdem sich Banquo und Fleance verabschiedet haben, erscheint vor Macbeth\u2019 Augen pl\u00f6tzlich ein schwebender, blutbefleckter Dolch. Er deutet dies als \u00fcberirdisches Zeichen und Aufforderung zur Tat und vollzieht sie, als Lady Macbeth eine als Signal vereinbarte Glocke l\u00e4utet.\n\nAls Lady Macbeth, die die Wachen des K\u00f6nigs zuvor mit einem Schlafmittel bet\u00e4ubt hat, im Burghof erscheint, um nach ihrem Mann zu sehen, findet sie einen v\u00f6llig verst\u00f6rten Macbeth vor. Zum Entsetzen seiner Frau tr\u00e4gt er die Mordwaffen noch bei sich, statt diese wie vereinbart den schlafenden Wachen in die Hand gedr\u00fcckt zu haben. Da er sich strikt weigert, die Kammer mit der blut\u00fcberstr\u00f6mten Leiche des K\u00f6nigs zum zweiten Male zu betreten, um die Dolche dorthin zu bringen, nimmt Lady Macbeth sich selbst des Plans an. Nach ihrer R\u00fcckkehr ist pl\u00f6tzlich vom Burgtor her ein ungest\u00fcmes Pochen zu vernehmen. Schnell verschwinden die beiden, um ihre H\u00e4nde vom Blut zu s\u00e4ubern und sich ihre Nachtgew\u00e4nder anzulegen.\n\nMittlerweile ist der zu dieser fr\u00fchen Morgenstunde \u00e4u\u00dferst missgelaunte Burgpf\u00f6rtner wach geworden und \u00f6ffnet das Tor \u2013 nicht ohne den drau\u00dfen wartenden Macduff und Lennox noch viele Male vergeblich klopfen zu lassen \u2013, um die beiden endlich einzulassen. Als Macbeth, angeblich durch den L\u00e4rm geweckt, am Tor erscheint, erkundigt sich Macduff nach dem Befinden Duncans, woraufhin Macbeth ihn zum Gemach des K\u00f6nigs f\u00fchrt. Macduff entdeckt den Mord, schl\u00e4gt Alarm und versetzt die gesamte Hofgesellschaft in helle Aufregung. In der allgemeinen Verwirrung erschl\u00e4gt Macbeth die zwei Kammerdiener Duncans als die mutma\u00dflichen M\u00f6rder. W\u00e4hrend Macduff durch diese Tat Verdacht sch\u00f6pft, beschlie\u00dfen die S\u00f6hne des K\u00f6nigs, Donalbain und Malcolm, nach Irland bzw. England zu fliehen, weil sie Angst haben, ebenfalls ermordet und zudem verd\u00e4chtigt zu werden, ihren Vater get\u00f6tet zu haben.\n\n Akt III \nErst im 3. Akt folgt dann der Wendepunkt der Handlung, als Macbeth Gelegenheit hat, sein Handeln zu \u00fcberdenken und beschlie\u00dft, nicht klein beizugeben. Er ordnet die Ermordung seines Freundes Banquo an. Aber die sich sammelnde Opposition gegen den Usurpator l\u00e4utet Macbeths Verderben ein.\n\nNach Duncans Tod und der Flucht seiner S\u00f6hne wird Macbeth als dritter in der Thronfolge zum K\u00f6nig gekr\u00f6nt. Er f\u00fcrchtet aber um seine Position, zum einen, weil Banquo von den Hexen wei\u00df, zum anderen, weil nach deren Prophezeiung nicht Macbeth Stammvater der k\u00f6niglichen Linie sein wird. Er schickt M\u00f6rder aus, um Banquo und dessen Sohn Fleance ermorden zu lassen. Zwar gelingt es ihnen, Banquo zu t\u00f6ten, aber Fleance kann entkommen. Als Macbeth das erf\u00e4hrt, reagiert er ungehalten, da er nun weiterhin um seine K\u00f6nigsherrschaft f\u00fcrchten muss.\n\nAm selben Abend gibt Macbeth ein Bankett zur Feier seiner Kr\u00f6nung. Als dazu der Geist Banquos erscheint und auf dem Stuhl von Macbeth Platz nimmt, zeigt sich der K\u00f6nig ver\u00e4ngstigt und verwirrt. Da aber nur er selbst Banquo wahrnimmt, ist die Gesellschaft h\u00f6chst beunruhigt durch das merkw\u00fcrdige Verhalten des K\u00f6nigs, der vor einem leeren Stuhl zur\u00fcckschreckt. Lady Macbeth versucht, die Situation zu retten und die verr\u00e4terischen Ausrufe ihres Mannes zu besch\u00f6nigen, indem sie seine Halluzinationen zun\u00e4chst als vor\u00fcbergehende und harmlose Familienkrankheit entschuldigt. Doch als sich der Vorfall wiederholt, bricht sie die Feier ab und schickt die G\u00e4ste nach Hause.\n\nAngesichts dieser Ereignisse beschlie\u00dft Macbeth, die drei Hexen ein zweites Mal aufzusuchen, um sich Gewissheit \u00fcber seine Zukunft zu verschaffen.\n\n Akt IV \nDer 4. Akt verz\u00f6gert die unausweichliche Aufl\u00f6sung, indem Macbeth durch die zweite Prophezeiung einen Hoffnungsschimmer erh\u00e4lt, er k\u00f6nnte dem Untergang entgehen.\n\nIn einer Grotte brauen die Hexen einen Zaubertrank, als \u2013 nach den Worten der zweiten Hexe \u201eSomething wicked this way comes\u201c (Etwas \u00dcbles kommt des Weges) \u2013 Macbeth an die T\u00fcr klopft, hereintritt und die alten Weiber bittet, ihm sein weiteres Schicksal zu weissagen. Daraufhin beschw\u00f6ren die Hexen drei Erscheinungen herauf: Die erste, ein bewaffnetes Haupt, weist ihn an, sich vor Macduff in acht zu nehmen. Die zweite, ein blutiges Kind, verk\u00fcndet ihm, dass kein Mensch, der von einer Frau geboren wurde, ihm je Schaden zuf\u00fcgen kann. Die dritte Vision, ein gekr\u00f6ntes Kind mit einem Baum in der Hand, verspricht Macbeth, er habe nichts zu f\u00fcrchten, solange nicht der Wald von Birnam nach Dunsinane kommt. Der K\u00f6nig ist erfreut \u00fcber diese neuen Prophezeiungen, dr\u00e4ngt die Hexen jedoch, ihm auch noch zu verraten, ob Banquos Nachkommen wirklich K\u00f6nige sein werden. Daraufhin konfrontieren die drei Schwestern Macbeth mit weiteren Erscheinungen: acht Figuren, gekleidet wie K\u00f6nige und augenscheinlich Nachfahren Banquos, und schlie\u00dflich auch Banquo selbst als letzten der Reihe. Mit dieser Vision verschwinden die Hexen und lassen Macbeth allein zur\u00fcck.\n\nLennox tritt auf und berichtet dem K\u00f6nig, dass Macduff nach England geflohen ist, um mit Malcolm ein Rebellionsheer gegen Macbeth anzuf\u00fchren. Aus Rache befiehlt dieser, Macduffs Frau und Kinder zu ermorden. Macduff, der in England mit Malcolm und K\u00f6nig Edward ein B\u00fcndnis gegen Macbeth schmiedet, sinnt auf Rache, als er von der Tat erf\u00e4hrt. Zusammen mit Malcolm und Siward, dem Earl of Northumberland und englischen Heerf\u00fchrer, zieht Macduff in den Krieg gegen Macbeth.\n\n Akt V \nDer 5. Akt l\u00f6st den zentralen Konflikt des St\u00fcckes auf.\n\nAuf Burg Dunsinane erscheint Macbeth als verbitterter Tyrann, w\u00e4hrend seine Frau, vom schlechten Gewissen wegen ihrer Schuld an Duncans Tod geplagt, an Albtr\u00e4umen leidet und im Schlaf wandelt und phantasiert, bis sie schlie\u00dflich den Verstand verliert und sich das Leben nimmt. Damit sind alle fr\u00fcheren Vertrauten und Freunde des K\u00f6nigs entweder geflohen oder tot.\n\nDie herannahenden Truppen verbergen sich hinter tarnenden \u00c4sten und Zweigen aus dem Wald von Birnam, um unbemerkt bis Dunsinane vordringen zu k\u00f6nnen. Als Macbeth von dem \u201ewandelnden Wald\u201c erf\u00e4hrt, erkennt er, dass sich dieser Teil der Prophezeiung erf\u00fcllen wird.\n\nZun\u00e4chst vermag aber niemand, den K\u00f6nig zu t\u00f6ten. Schlie\u00dflich stellt sich Macduff Macbeth zum Zweikampf. Auf die h\u00f6hnische \u00c4u\u00dferung des Tyrannen, kein Mensch, der von einer Frau geboren wurde, sei imstande, ihn zu t\u00f6ten, erwidert Macduff, er sei nicht von seiner Mutter geboren, sondern ihr vor der Zeit aus dem Bauch geschnitten worden. Macbeth weigert sich dennoch, sich zu ergeben, und wird im Zweikampf von Macduff get\u00f6tet. Anschlie\u00dfend wird Duncans Sohn Malcolm zum neuen K\u00f6nig von Schottland ausgerufen."
      ],
      "es":[
         " Acto I \n\nLa obra comienza con tres brujas, las tres \"Hermanas Fat\u00eddicas\" hacen un hechizo en el que se ponen de acuerdo acerca de su pr\u00f3ximo encuentro con Macbeth. En la escena siguiente, Duncan, rey de Escocia, comenta con sus oficiales el aplastamiento de la invasi\u00f3n de Escocia por noruegos e irlandeses, acaudillados por el rebelde Macdonwald, en la cual Macbeth, thane (bar\u00f3n) de Glamis y primo del rey, ha tenido un importante papel. Duncan se propone darle en recompensa el t\u00edtulo de thane de Cawdor.\n\nMacbeth y Banquo con las brujas por Johann Heinrich F\u00fcssli\nCuando Macbeth y su compa\u00f1ero Banquo cabalgan hacia Forres desde el campo de batalla, se encuentran con las brujas, quienes saludan a Macbeth, primero como thane de Glamis, luego como thane de Cawdor, y por \u00faltimo anunci\u00e1ndole que un d\u00eda ser\u00e1 rey.  A Banquo le dicen que sus descendientes ser\u00e1n reyes. Cuando Macbeth pide a las brujas que le aclaren el sentido de las profec\u00edas, ellas desaparecen. Se presenta un enviado del rey (Ross), quien notifica a Macbeth la concesi\u00f3n real del t\u00edtulo de thane de Cawdor.\n\nViendo cumplida la profec\u00eda de las brujas, Macbeth comienza a ambicionar el trono. Macbeth escribe una carta a su esposa, en Inverness, explicando las profec\u00edas de las brujas. Lady Macbeth, al leer la carta, concibe el prop\u00f3sito de asesinar al rey Duncan para lograr que su marido llegue a ser rey. De improviso se presenta Macbeth en el castillo, as\u00ed como la noticia de que Duncan va a pasar all\u00ed esa noche. Lady Macbeth le expone sus planes. Macbeth duda, pero su esposa lo ciza\u00f1a, estimulando su ambici\u00f3n.\n\n Acto II \n\nAl llegar la noche, Macbeth, instigado por su c\u00f3nyuge, da muerte al rey Duncan cuando duerme en su aposento. Antes de su muerte ve visiones de una espada con sangre y siente fuertes remordimientos, que Lady Macbeth se esfuerza por acallar, y ve lo d\u00e9bil que es su esposo y decide ella incriminar a los criados ti\u00f1\u00e9ndolos de sangre. A la ma\u00f1ana siguiente, se descubre el crimen y Macbeth culpa a los sirvientes de Duncan, a los que previamente ha asesinado, supuestamente en un arrebato de furia para vengar la muerte del rey. Los hijos de Duncan, Malcolm y Donalbain, que se encuentran tambi\u00e9n en el castillo, no creen la versi\u00f3n de Macbeth, pero disimulan para evitar ser tambi\u00e9n asesinados. Malcolm huye a Inglaterra y Donalbain, a Irlanda.\n\nGracias a su parentesco con el fallecido rey Duncan y a la huida de los hijos de este, Macbeth consigue ser proclamado rey de Escocia, cumpli\u00e9ndose as\u00ed la segunda profec\u00eda de las brujas.\n\n Acto III \n\nA pesar del \u00e9xito de sus prop\u00f3sitos, Macbeth contin\u00faa intranquilo a causa de la profec\u00eda que las brujas hicieron a Banquo, seg\u00fan la cual este ser\u00eda padre de reyes. Encarga a unos asesinos que acaben con su vida, y la de su hijo, Fleance, cuando lleguen al castillo para participar en un banquete al que Macbeth les ha invitado. Los asesinos matan a Banquo, pero Fleance consigue huir del lugar. En el banquete, poco despu\u00e9s de que Macbeth sepa por los asesinos lo ocurrido, se aparece el espectro de Banquo y se sienta en el sitio de Macbeth. S\u00f3lo Macbeth puede ver al fantasma, con el que dialoga, y en sus palabras se hace evidente su crimen.\n\n Acto IV \n\nEscena de Macbeth: el conjuro de las brujas (acto IV, escena I). Cuadro de William Rimmer\nMacbeth regresa al lugar de su encuentro con las brujas. Inquieto, les pregunta por su futuro. Ellas conjuran a tres esp\u00edritus. El primero advierte a Macbeth que tenga cuidado con Macduff. El segundo dice que \"ning\u00fan hombre nacido de mujer\" podr\u00e1 vencer a Macbeth, y el tercero hace una curiosa profec\u00eda:\n\nEstas profec\u00edas tranquilizan a Macbeth, pero no se queda satisfecho. Quiere saber tambi\u00e9n si los descendientes de Banquo llegar\u00e1n a reinar, como las brujas profetizaron. En respuesta a su demanda, se aparecen los fantasmas de ocho reyes y el de Banquo, con un espejo en la mano, indicando as\u00ed que ocho descendientes de Banquo ser\u00edan reyes de Escocia. Un vasallo de Macbeth le notifica que Macduff ha desertado. En represalia, Macbeth decide atacar su castillo y acabar con la vida de toda su familia. La acci\u00f3n se traslada a Inglaterra, donde Macduff, ignorante todav\u00eda de la suerte que ha corrido su familia, se entrevista con Malcolm, hijo de Duncan, al que intenta convencer para que reclame el trono. Recibe la noticia de la muerte de su familia.\n\n Acto V \n\nLady Macbeth son\u00e1mbula por Johann Heinrich F\u00fcssli\nLady Macbeth empieza a sufrir remordimientos: son\u00e1mbula, intenta lavar manchas de sangre imaginarias de sus manos. Malcolm y Macduff, con la ayuda de Inglaterra, invaden Escocia. Macduff, Malcolm y el ingl\u00e9s Siward, conde de Northumberland, atacan el castillo de Dunsinane, con un ej\u00e9rcito camuflado con ramas del bosque de Birnam, con lo que se cumple una de las profec\u00edas de las brujas: el bosque de Birnam se mueve y ataca Dunsinane. Macbeth recibe la noticia de que el bosque se mueve y de la muerte de su esposa por suicidio. Tras pronunciar un mon\u00f3logo nihilista, toma la determinaci\u00f3n de combatir hasta el final. Tras matar al hijo de Siward, se enfrenta con Macduff. Se siente todav\u00eda seguro, a causa de la profec\u00eda de las brujas, pero ya era demasiado tarde, debido a que Macduff le revela que su madre hab\u00eda muerto una hora antes de que \u00e9l naciera, y que los m\u00e9dicos hab\u00edan realizado una ces\u00e1rea para mantener a Macduff vivo, y as\u00ed se cumple la profec\u00eda de que \u00abno podr\u00eda ser matado por ning\u00fan hombre nacido de mujer\u00bb y Macbeth comprende que las profec\u00edas de las brujas han tenido algunos significados ocultos. Acto seguido, Macduff mata a Macbeth y le decapita su cabeza. En la escena final, Malcolm es coronado rey de Escocia. La profec\u00eda referente al destino real de los hijos de Banquo era familiar a los contempor\u00e1neos de Shakespeare, pues el rey Jacobo I de Inglaterra era considerado descendiente de Banquo."
      ],
      "it":[
         "Atto primo \nLa tragedia si apre in una cupa Scozia d'inizio Basso Medioevo, in un'atmosfera di lampi e tuoni; tre Streghe (Le Sorelle Fatali, ispirate certamente alle Norne del mito norreno e alle Parche/Moire della tradizione greco-romana) decidono che il loro prossimo incontro dovr\u00e0 avvenire in presenza di Macbeth. \n\nNella scena seguente, un sergente ferito riferisce al re Duncan di Scozia che i suoi generali, Macbeth e Banquo, hanno appena sconfitto le forze congiunte di Norvegia e Irlanda, guidate dal ribelle Macdonwald. Macbeth, congiunto del re, \u00e8 lodato per il suo coraggio e prodezza in battaglia.\n\nLa scena cambia: Macbeth e Banquo appaiono sulla scena, di ritorno ai loro castelli, facendo considerazioni sulla vittoria appena conseguita e sul tempo \"brutto e bello insieme\", che caratterizza la natura ambigua e carica di soprannaturale della brughiera desolata e pervasa di nebbia che stanno attraversando. Le tre streghe, che li stavano aspettando, compaiono e pronunciano profezie. Anche se Banquo per primo le sfida, esse si rivolgono a Macbeth. La prima lo saluta come \"Macbeth, sire di Glamis\", titolo che Macbeth gi\u00e0 possiede, la seconda come \"Macbeth, sire di Cawdor\", titolo che non possiede ancora, e la terza \"Macbeth, il Re\". Macbeth \u00e8 stupefatto e silenzioso, cos\u00ec Banquo ancora una volta tenta di fronteggiarle, intimorito dall'aspetto delle Sorelle Fatali e dalle condizioni particolari e misteriose del momento. Le streghe dunque informano anche Banquo di una profezia, affermando che sar\u00e0 il capostipite di una dinastia di re. Poi le tre streghe svaniscono, lasciando nel dubbio Macbeth e Banquo sulla reale natura di quella strana apparizione.\n\nSopraggiunge dunque il  re, che annuncia a Macbeth la concessione a suo favore del titolo di generale dell'armata Scozzese: la prima profezia \u00e8 cos\u00ec realizzata. Immediatamente Macbeth incomincia a nutrire l'ambizione di diventare re.\n\nMacbeth scrive alla moglie (Lady Macbeth) riguardo alle profezie delle tre streghe.\n\nQuando Duncan decide di soggiornare al castello di Macbeth a Inverness, Lady Macbeth escogita un piano per ucciderlo e assicurare il trono di Scozia al marito. Anche se Macbeth mostra dei tentennamenti, volendo ritornare sui propri passi e smentendo le ambizioni manifestate nella lettera inviata alla moglie, Lady Macbeth alla fine lo persuade a seguire il piano.\n\nNella notte della visita, Lady Macbeth ubriaca le guardie del re, facendole cadere in un pesante sonno. Macbeth, con un noto soliloquio che lo porta a vedere di fronte a s\u00e9 l'allucinazione di un pugnale insanguinato che lo guida verso l'omicidio del suo stesso re e cugino, si introduce nelle stanze di Duncan e lo pugnala a morte. Sconvolto dall'atto si rifugia da Lady Macbeth, la quale invece non si perde d'animo e recupera la situazione lasciando la coppia di armi usate per l'assassinio presso i corpi addormentati delle guardie, imbrattando i loro volti, le mani e le vesti col sangue del re. \n\nAl mattino, poco dopo l'arrivo di MacDuff, nobile scozzese venuto a recare omaggio al sovrano, viene scoperto l'omicidio. In un simulato attacco di rabbia, Macbeth uccide le guardie prima che queste possano rivendicare la loro innocenza.\n\nAtto secondo\nMacDuff \u00e8 subito dubbioso riguardo alla condotta di Macbeth, ma non rivela i propri sospetti pubblicamente. Temendo per la propria vita, il figlio di Duncan, Malcolm, scappa in Inghilterra. Su questi presupposti Macbeth, per la sua parentela con Duncan, sale al trono di Scozia.\n\nA dispetto del suo successo, Macbeth non \u00e8 a suo agio circa la profezia per cui Banquo sarebbe diventato il capostipite di una dinastia di re, temendo di essere a sua volta scalzato. Cos\u00ec lo invita a un banchetto reale e viene a sapere che Banquo e il giovane figlio, Fleance, usciranno per una cavalcata quella sera stessa. Macbeth ingaggia due sicari per uccidere Banquo e Fleance (un terzo sicario compare misteriosamente nel parco prima dell'omicidio: secondo una parte della critica potrebbe essere immagine e personificazione stessa dello spirito dell'Assassinio). Banquo viene dunque massacrato brutalmente, ma Fleance riesce a fuggire. Al banchetto, che dovrebbe celebrare il trionfo del re, Macbeth \u00e8 convinto di vedere il fantasma di Banquo che siede al suo posto, mentre gli astanti e la stessa Lady Macbeth non vedono nulla. Il resto dei convitati \u00e8 spaventato dalla furia di Macbeth verso un seggio vuoto, finch\u00e9 una disperata Lady Macbeth ordina a tutti di andare via.\n\nAtto terzo\nMacbeth, che cammina ormai a cavallo fra mondo del reale e mondo soprannaturale, si reca dalle streghe in cerca di certezze. Esse, interrogate, chiamano a rispondere degli spiriti: una testa armata dice a Macbeth \"temi MacDuff\", un bambino insanguinato gli dice \"nessun nato di donna pu\u00f2 nuocerti\", un bambino incoronato gli dice \"Macbeth non sar\u00e0 sconfitto fino a che la foresta di Birnam non muova verso Dunsinane\"; infine appare un corteo di otto spiriti a simboleggiare i discendenti di Banquo, alla vista dei quali Macbeth si dispera.\n\nSi avvia una stagione di sanguinaria persecuzione ai danni di tutti i lord di Scozia che il sovrano ritiene sospetti, e in particolare contro MacDuff. Un gruppo di sicari viene inviato al suo castello per ucciderlo, ma una volta l\u00ec i mercenari non lo trovano, essendo questi recatosi in Inghilterra per cercare aiuto militare contro Macbeth e avviare una rivolta. Gli assassini a ogni modo perpetrano il massacro della moglie di MacDuff e dei suoi figli, in una scena piena di patetismo e crudelt\u00e0.\n\nLady Macbeth nel frattempo, incapace di raggiungere il marito nelle dimensioni surreali in cui si \u00e8 perso, non regge pi\u00f9 il peso dei suoi delitti e comincia a essere tormentata da visioni e incubi che sconvolgono il suo sonno, portandola a episodi di sonnambulismo che sfociano in crisi disperate dove tenta di ripulire le mani da macchie di sangue incancellabili.\n\nAtto quarto\nIn Inghilterra MacDuff e Malcolm pianificano l'invasione della Scozia. Macbeth, adesso identificato come un tiranno, vede che molti baroni disertano dal suo fianco. Malcolm guida un esercito con MacDuff e Seyward, conte di Northumbria, contro il castello di Dunsinane, fortezza associata al trono di Scozia dove Macbeth risiede. Ai soldati, accampati nel bosco di Birnam, viene ordinato di tagliare i rami degli alberi per mascherare il loro numero. Con ci\u00f2 si realizza la terza profezia delle streghe: tenendo alti i rami degli alberi, innumerevoli soldati rassomigliano al bosco di Birnam che avanza verso Dunsinane. Alla notizia della morte della moglie (la cui causa non \u00e8 chiara; si presume che ella si sia suicidata, oppure che sia caduta da una torre in preda al delirio da sonnambula) e di fronte all'avanzata dell'esercito ribelle, Macbeth pronuncia il famoso soliloquio (\"Domani e domani e domani\"), sul senso vacuo della vita e di tutte le azioni che la costellano, vani atti insignificanti che puntano al raggiungimento di obiettivi che non hanno alcun reale valore.\n\nRichiede poi che gli siano portate armi e armatura, pronto a vendere cara la pelle in quello che gi\u00e0 sente essere il suo atto finale.\n\nLa battaglia infuria sotto le mura di Dunsinane, e il giovane Seyward, alleato di MacDuff, muore per mano del tiranno, il quale poi affronta MacDuff. Macbeth ritiene di non avere alcun motivo di temere il lord ribelle perch\u00e9 non pu\u00f2 essere ferito o ucciso da \"nessuno nato da donna\", secondo la profezia delle streghe. MacDuff per\u00f2 dichiara di \"essere stato strappato prima del tempo dal ventre di sua madre\" e che quindi non era propriamente \"nato\" da donna. Macbeth tuttavia, nella furia della battaglia accetta tale destino e non dimostra neanche un momento di cedimento, nella sua lucida follia. I due combattono e MacDuff decapita Macbeth, realizzando cos\u00ec l'ultima delle profezie.\n\nAnche se Malcolm, e non Fleance, sal\u00ed al trono, la profezia delle streghe riguardante Banquo fu ritenuta veritiera dal pubblico di Shakespeare, che riteneva che re Giacomo I fosse diretto discendente di Banquo."
      ]
   },
}
```

Where:

_title_ stores the titles of Wikipedia pages corresponding to each language.

_section_ contains the section titles from which the summaries are extracted (specific to Echo-Wiki).

_versions_ is the list of filepaths that provide access to the available book texts in multiple languages.

_summaries_ holds the available summaries for each language.


## License

This work is under the [Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) license](https://creativecommons.org/licenses/by-nc-sa/4.0/).
