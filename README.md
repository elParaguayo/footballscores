footballscores
==============

I'll add a bit more detail here when I have time, but in the meantime, here's some sample output from the module.

>>> from footballscores import FootballMatch
>>> a=FootballMatch("Osasuna", detailed=True)
>>> print a
Osasuna 1-5 Athletic Bilbao (FT)
>>> print a.PrintDetail
(FT) Osasuna 1-5 Athletic Bilbao (Osasuna: E.Armenteros (10') - Athletic Bilbao: M.Susaeta (3'), A.Aduriz (16', 62'), I.G贸mez (84'), E.Sola Clemente (88'))
>>> a.HomeScorers
[(u'E.Armenteros', [u"10'"])]
>>> a.AwayScorers
[(u'M.Susaeta', [u"3'"]), (u'A.Aduriz', [u"16'", u"62'"]), (u'I.G\u8d38mez', [u"84'"]), (u'E.Sola Clemente', [u"88'"])]
>>> a.HomeYellowCards
[(u'J.Loties', [u"21'"]), (u'F.Silva', [u"47'"]), (u'Acu\u5e3da', [u"65'"]), (u'A.Arribas', [u"71'"])]
>>> a.AwayYellowCards
[(u'A.Iturraspe', [u"19'"]), (u'A.Aduriz', [u"27'"]), (u'C.Gurpegi', [u"51'"]), (u'M.Balenziaga', [u"72'"])]
>>> a.HomeRedCards
[(u'A.Arribas', [u"76'"])]
>>> a.AwayRedCards
[]
>>> a.MatchTime
'FT'
