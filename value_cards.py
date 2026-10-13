"""
Набор из 100 карточек ценностей для PsychoMirror.

Основа: Personal Values Card Sort, update 2011
(W. R. Miller, J. C'de Baca, D. B. Matthews, P. L. Wilbourne, University of New Mexico).
Инструмент в public domain: «may be copied or adapted without further permission».

Что взято из оригинала без изменений:
  - состав и нумерация 100 карточек, английские названия и определения (verbatim,
    сверено программно с PDF; у BELONGING определение обрывается так же, как в оригинале).
Что добавлено нами (адаптация, НЕ валидировано):
  - name_ru / def_ru, name_hu / def_hu — авторский перевод (RU — гендерно-нейтральный);
    перед полевым использованием нужен обратный перевод и когнитивные интервью.
  - schwartz — привязка к 19 ценностям уточнённой теории Шварца (Schwartz et al., 2012)
    по экспертной оценке; confidence показывает, насколько привязка однозначна.
    OUTSIDE — ценность вне круговой модели Шварца (не форсируем).
  - sensitive — карточки, которые в рабочем/HR-контексте лучше исключать или делать опциональными.

Запуск `python value_cards.py` проверяет набор и пишет value_cards_100.csv.
"""

import csv
from collections import Counter
from pathlib import Path

# --- Уточнённая теория базовых ценностей Шварца (2012): 19 ценностей -> 4 полюса высшего порядка
SCHWARTZ_19 = {
    "SD-T": ("Self-direction–thought", "Самостоятельность мысли", "OPENNESS"),
    "SD-A": ("Self-direction–action", "Самостоятельность действий", "OPENNESS"),
    "ST":   ("Stimulation", "Стимуляция", "OPENNESS"),
    "HE":   ("Hedonism", "Гедонизм", "OPENNESS/SELF_ENHANCEMENT"),
    "AC":   ("Achievement", "Достижение", "SELF_ENHANCEMENT"),
    "PO-D": ("Power–dominance", "Власть над людьми", "SELF_ENHANCEMENT"),
    "PO-R": ("Power–resources", "Власть над ресурсами", "SELF_ENHANCEMENT"),
    "FA":   ("Face", "Репутация, «лицо»", "SELF_ENHANCEMENT/CONSERVATION"),
    "SE-P": ("Security–personal", "Личная безопасность", "CONSERVATION"),
    "SE-S": ("Security–societal", "Общественная безопасность", "CONSERVATION"),
    "TR":   ("Tradition", "Традиция", "CONSERVATION"),
    "CO-R": ("Conformity–rules", "Конформность: правила", "CONSERVATION"),
    "CO-I": ("Conformity–interpersonal", "Конформность: межличностная", "CONSERVATION"),
    "HU":   ("Humility", "Скромность", "CONSERVATION/SELF_TRANSCENDENCE"),
    "BE-D": ("Benevolence–dependability", "Благожелательность: надёжность", "SELF_TRANSCENDENCE"),
    "BE-C": ("Benevolence–caring", "Благожелательность: забота", "SELF_TRANSCENDENCE"),
    "UN-C": ("Universalism–concern", "Универсализм: забота о мире", "SELF_TRANSCENDENCE"),
    "UN-N": ("Universalism–nature", "Универсализм: природа", "SELF_TRANSCENDENCE"),
    "UN-T": ("Universalism–tolerance", "Универсализм: терпимость", "SELF_TRANSCENDENCE"),
    "OUTSIDE": ("Outside the circumplex", "Вне модели Шварца", None),
}

# Противоположные полюса круговой модели — основа для поиска ценностных конфликтов
OPPOSING_POLES = [("OPENNESS", "CONSERVATION"), ("SELF_ENHANCEMENT", "SELF_TRANSCENDENCE")]

# (id, key, name_en, def_en, name_ru, def_ru, schwartz, confidence, sensitive)
_ROWS = [
    (1, "ACCEPTANCE", "ACCEPTANCE", "to be accepted as I am",
     "ПРИНЯТИЕ", "чтобы окружающие принимали меня без попыток переделать", "OUTSIDE", "low", ""),
    (2, "ACCURACY", "ACCURACY", "to be correct in my opinions and beliefs",
     "ТОЧНОСТЬ СУЖДЕНИЙ", "придерживаться верных мнений и убеждений", "SD-T", "low", ""),
    (3, "ACHIEVEMENT", "ACHIEVEMENT", "to have important accomplishments",
     "ДОСТИЖЕНИЯ", "добиваться значимых результатов", "AC", "high", ""),
    (4, "ADVENTURE", "ADVENTURE", "to have new and exciting experiences",
     "ПРИКЛЮЧЕНИЯ", "получать новые и захватывающие впечатления", "ST", "high", ""),
    (5, "ART", "ART", "to appreciate or express myself in art",
     "ИСКУССТВО", "ценить искусство или выражать себя через него", "OUTSIDE", "low", ""),
    (6, "ATTRACTIVENESS", "ATTRACTIVENESS", "to be physically attractive",
     "ПРИВЛЕКАТЕЛЬНОСТЬ", "иметь привлекательную внешность", "FA", "low", ""),
    (7, "AUTHORITY", "AUTHORITY", "to be in charge of others",
     "РУКОВОДСТВО", "стоять во главе других людей и отвечать за них", "PO-D", "high", ""),
    (8, "AUTONOMY", "AUTONOMY", "to be self-determined and independent",
     "АВТОНОМИЯ", "самостоятельно определять свою жизнь", "SD-A", "high", ""),
    (9, "BEAUTY", "BEAUTY", "to appreciate beauty around me",
     "КРАСОТА", "замечать и ценить красоту вокруг", "UN-N", "medium", ""),
    (10, "BELONGING", "BELONGING", "to have a sense of belonging, being part of",
     "ПРИНАДЛЕЖНОСТЬ", "чувствовать себя частью общности", "SE-P", "medium", ""),
    (11, "CARING", "CARING", "to take care of others",
     "ЗАБОТА", "заботиться о других", "BE-C", "high", ""),
    (12, "CHALLENGE", "CHALLENGE", "to take on difficult tasks and problems",
     "ВЫЗОВ", "браться за трудные задачи и проблемы", "ST", "medium", ""),
    (13, "COMFORT", "COMFORT", "to have a pleasant and comfortable life",
     "КОМФОРТ", "жить приятно и удобно", "HE", "medium", ""),
    (14, "COMMITMENT", "COMMITMENT", "to make enduring, meaningful commitments",
     "ПРИВЕРЖЕННОСТЬ", "брать на себя долгосрочные и значимые обязательства", "BE-D", "medium", ""),
    (15, "COMPASSION", "COMPASSION", "to feel and act on concern for others",
     "СОСТРАДАНИЕ", "сочувствовать другим и действовать исходя из этого", "UN-C", "medium", ""),
    (16, "COMPLEXITY", "COMPLEXITY", "to embrace the intricacies of life",
     "СЛОЖНОСТЬ", "принимать запутанность и многогранность жизни", "SD-T", "medium", ""),
    (17, "COMPROMISE", "COMPROMISE", "to be willing to give and take in reaching agreements",
     "КОМПРОМИСС", "уступать и договариваться, чтобы прийти к согласию", "CO-I", "medium", ""),
    (18, "CONTRIBUTION", "CONTRIBUTION", "to make a lasting contribution in the world",
     "ВКЛАД", "внести в мир долговременный вклад", "UN-C", "medium", ""),
    (19, "COOPERATION", "COOPERATION", "to work collaboratively with others",
     "СОТРУДНИЧЕСТВО", "работать сообща с другими", "BE-C", "low", ""),
    (20, "COURAGE", "COURAGE", "to be brave and strong in the face of adversity",
     "СМЕЛОСТЬ", "сохранять мужество и стойкость перед лицом трудностей", "OUTSIDE", "low", ""),
    (21, "COURTESY", "COURTESY", "to be considerate and polite toward others",
     "ВЕЖЛИВОСТЬ", "проявлять к другим внимание и учтивость", "CO-I", "high", ""),
    (22, "CREATIVITY", "CREATIVITY", "to create new things or ideas",
     "ТВОРЧЕСТВО", "создавать новые вещи или идеи", "SD-T", "high", ""),
    (23, "CURIOSITY", "CURIOSITY", "to seek out, experience, and learn new things",
     "ЛЮБОЗНАТЕЛЬНОСТЬ", "искать, пробовать и узнавать новое", "SD-T", "high", ""),
    (24, "DEPENDABILITY", "DEPENDABILITY", "to be reliable and trustworthy",
     "НАДЁЖНОСТЬ", "заслуживать доверия, чтобы на меня можно было положиться", "BE-D", "high", ""),
    (25, "DILIGENCE", "DILIGENCE", "to be thorough and conscientious in whatever I do",
     "ДОБРОСОВЕСТНОСТЬ", "делать любое дело основательно и тщательно", "AC", "medium", ""),
    (26, "DUTY", "DUTY", "to carry out my duties and obligations",
     "ДОЛГ", "выполнять свои обязанности и обязательства", "CO-R", "medium", ""),
    (27, "ECOLOGY", "ECOLOGY", "to live in harmony with the environment",
     "ЭКОЛОГИЯ", "жить в гармонии с природой", "UN-N", "high", ""),
    (28, "EXCITEMENT", "EXCITEMENT", "to have a life full of thrills and stimulation",
     "ОСТРЫЕ ОЩУЩЕНИЯ", "жить жизнью, полной ярких переживаний и встрясок", "ST", "high", ""),
    (29, "FAITHFULNESS", "FAITHFULNESS", "to be loyal and true in relationships",
     "ВЕРНОСТЬ", "хранить верность и преданность в отношениях", "BE-D", "high", ""),
    (30, "FAME", "FAME", "to be known and recognized",
     "СЛАВА", "иметь известность и признание", "FA", "medium", ""),
    (31, "FAMILY", "FAMILY", "to have a happy, loving family",
     "СЕМЬЯ", "иметь счастливую, любящую семью", "SE-P", "medium", ""),
    (32, "FITNESS", "FITNESS", "to be physically fit and strong",
     "ФИЗИЧЕСКАЯ ФОРМА", "поддерживать силу и хорошую физическую форму", "OUTSIDE", "low", ""),
    (33, "FLEXIBILITY", "FLEXIBILITY", "to adjust to new circumstances easily",
     "ГИБКОСТЬ", "легко приспосабливаться к новым обстоятельствам", "OUTSIDE", "low", ""),
    (34, "FORGIVENESS", "FORGIVENESS", "to be forgiving of others",
     "ПРОЩЕНИЕ", "уметь прощать других", "BE-C", "high", ""),
    (35, "FREEDOM", "FREEDOM", "to be free from undue restrictions and limitations",
     "СВОБОДА", "жить без лишних ограничений и запретов", "SD-A", "high", ""),
    (36, "FRIENDSHIP", "FRIENDSHIP", "to have close, supportive friends",
     "ДРУЖБА", "иметь близких друзей, на которых можно опереться", "BE-C", "high", ""),
    (37, "FUN", "FUN", "to play and have fun",
     "ВЕСЕЛЬЕ", "играть и веселиться", "HE", "high", ""),
    (38, "GENEROSITY", "GENEROSITY", "to give what I have to others",
     "ЩЕДРОСТЬ", "делиться с другими тем, что у меня есть", "BE-C", "medium", ""),
    (39, "GENUINENESS", "GENUINENESS", "to act in a manner that is true to who I am",
     "ПОДЛИННОСТЬ", "поступать в согласии с тем, кто я есть на самом деле", "SD-A", "low", ""),
    (40, "GODS_WILL", "GOD'S WILL", "to seek and obey the will of God",
     "БОЖЬЯ ВОЛЯ", "искать волю Бога и следовать ей", "TR", "high", "religion"),
    (41, "GRATITUDE", "GRATITUDE", "to be thankful and appreciative",
     "БЛАГОДАРНОСТЬ", "испытывать и выражать признательность", "OUTSIDE", "low", ""),
    (42, "GROWTH", "GROWTH", "to keep changing and growing",
     "РОСТ", "постоянно меняться и развиваться", "SD-T", "low", ""),
    (43, "HEALTH", "HEALTH", "to be physically well and healthy",
     "ЗДОРОВЬЕ", "сохранять здоровье и хорошее самочувствие", "SE-P", "high", ""),
    (44, "HONESTY", "HONESTY", "to be honest and truthful",
     "ЧЕСТНОСТЬ", "говорить правду и не обманывать", "BE-D", "high", ""),
    (45, "HOPE", "HOPE", "to maintain a positive and optimistic outlook",
     "НАДЕЖДА", "сохранять позитивный и оптимистичный взгляд", "OUTSIDE", "low", ""),
    (46, "HUMILITY", "HUMILITY", "to be modest and unassuming",
     "СКРОМНОСТЬ", "держаться скромно и без притязаний", "HU", "high", ""),
    (47, "HUMOR", "HUMOR", "to see the humorous side of myself and the world",
     "ЮМОР", "видеть смешное в себе и в мире", "OUTSIDE", "low", ""),
    (48, "IMAGINATION", "IMAGINATION", "to have dreams and see possibilities",
     "ВООБРАЖЕНИЕ", "мечтать и видеть возможности", "SD-T", "medium", ""),
    (49, "INDEPENDENCE", "INDEPENDENCE", "to be free from depending on others",
     "НЕЗАВИСИМОСТЬ", "не зависеть от других", "SD-A", "high", ""),
    (50, "INDUSTRY", "INDUSTRY", "to work hard and well at my life tasks",
     "ТРУДОЛЮБИЕ", "усердно и хорошо выполнять свои жизненные задачи", "AC", "medium", ""),
    (51, "INNER_PEACE", "INNER PEACE", "to experience personal peace",
     "ВНУТРЕННИЙ ПОКОЙ", "ощущать душевный покой", "OUTSIDE", "low", ""),
    (52, "INTEGRITY", "INTEGRITY", "to live my daily life in a way that is consistent with my values",
     "ЦЕЛОСТНОСТЬ", "жить каждый день в согласии со своими ценностями", "OUTSIDE", "low", ""),
    (53, "INTELLIGENCE", "INTELLIGENCE", "to keep my mind sharp and active",
     "ИНТЕЛЛЕКТ", "поддерживать ум острым и активным", "AC", "medium", ""),
    (54, "INTIMACY", "INTIMACY", "to share my innermost experiences with others",
     "БЛИЗОСТЬ", "делиться с другими самым сокровенным", "OUTSIDE", "low", ""),
    (55, "JUSTICE", "JUSTICE", "to promote fair and equal treatment for all",
     "СПРАВЕДЛИВОСТЬ", "добиваться честного и равного отношения ко всем", "UN-C", "high", ""),
    (56, "KNOWLEDGE", "KNOWLEDGE", "to learn and contribute valuable knowledge",
     "ЗНАНИЯ", "учиться и приумножать ценные знания", "SD-T", "medium", ""),
    (57, "LEADERSHIP", "LEADERSHIP", "to inspire and guide others",
     "ЛИДЕРСТВО", "вдохновлять и вести за собой других", "PO-D", "medium", ""),
    (58, "LEISURE", "LEISURE", "to take time to relax and enjoy",
     "ОТДЫХ", "находить время, чтобы расслабиться и насладиться жизнью", "HE", "high", ""),
    (59, "LOVED", "LOVED", "to be loved by those close to me",
     "ПОЛУЧАТЬ ЛЮБОВЬ", "чтобы меня любили близкие люди", "OUTSIDE", "low", ""),
    (60, "LOVING", "LOVING", "to give love to others",
     "ДАРИТЬ ЛЮБОВЬ", "отдавать любовь другим", "BE-C", "medium", ""),
    (61, "MASTERY", "MASTERY", "to be competent in my everyday activities",
     "МАСТЕРСТВО", "умело справляться со своими повседневными делами", "AC", "high", ""),
    (62, "MINDFULNESS", "MINDFULNESS", "to live conscious and mindful of the present moment",
     "ОСОЗНАННОСТЬ", "жить, осознавая настоящий момент", "OUTSIDE", "low", ""),
    (63, "MODERATION", "MODERATION", "to avoid excesses and find a middle ground",
     "УМЕРЕННОСТЬ", "избегать крайностей и находить золотую середину", "TR", "high", ""),
    (64, "MONOGAMY", "MONOGAMY", "to have one close, loving relationship",
     "МОНОГАМИЯ", "быть в близких любящих отношениях с одним партнёром", "OUTSIDE", "low", "intimate"),
    (65, "MUSIC", "MUSIC", "to enjoy or express myself in music",
     "МУЗЫКА", "наслаждаться музыкой или выражать себя через неё", "OUTSIDE", "low", ""),
    (66, "NON_CONFORMITY", "NON-CONFORMITY", "to question and challenge authority and norms",
     "НОНКОНФОРМИЗМ", "подвергать сомнению авторитеты и нормы", "SD-A", "medium", ""),
    (67, "NOVELTY", "NOVELTY", "to have a life full of change and variety",
     "НОВИЗНА", "жить жизнью, полной перемен и разнообразия", "ST", "high", ""),
    (68, "NURTURANCE", "NURTURANCE", "to encourage and support others",
     "ПОДДЕРЖКА", "ободрять и поддерживать других", "BE-C", "high", ""),
    (69, "OPENNESS", "OPENNESS", "to be open to new experiences, ideas, and options",
     "ОТКРЫТОСТЬ", "открываться новому опыту, идеям и возможностям", "SD-T", "medium", ""),
    (70, "ORDER", "ORDER", "to have a life that is well-ordered and organized",
     "ПОРЯДОК", "жить упорядоченно и организованно", "SE-P", "medium", ""),
    (71, "PASSION", "PASSION", "to have deep feelings about ideas, activities, or people",
     "СТРАСТЬ", "испытывать глубокие чувства к идеям, делам или людям", "OUTSIDE", "low", ""),
    (72, "PATRIOTISM", "PATRIOTISM", "to love, serve, and protect my country",
     "ПАТРИОТИЗМ", "любить свою страну, служить ей и защищать её", "SE-S", "medium", "political"),
    (73, "PLEASURE", "PLEASURE", "to feel good",
     "УДОВОЛЬСТВИЕ", "испытывать приятные ощущения", "HE", "high", ""),
    (74, "POPULARITY", "POPULARITY", "to be well-liked by many people",
     "ПОПУЛЯРНОСТЬ", "нравиться многим людям", "FA", "medium", ""),
    (75, "POWER", "POWER", "to have control over others",
     "ВЛАСТЬ", "контролировать других людей", "PO-D", "high", ""),
    (76, "PRACTICALITY", "PRACTICALITY", "to focus on what is practical, prudent, and sensible",
     "ПРАКТИЧНОСТЬ", "сосредотачиваться на практичном, разумном и осмотрительном", "OUTSIDE", "low", ""),
    (77, "PROTECT", "PROTECT", "to protect and keep safe those I love",
     "ЗАЩИТА", "защищать и оберегать тех, кого люблю", "SE-P", "medium", ""),
    (78, "PROVIDE", "PROVIDE", "to provide for and take care of my family",
     "ОБЕСПЕЧЕНИЕ СЕМЬИ", "обеспечивать свою семью и заботиться о ней", "SE-P", "low", ""),
    (79, "PURPOSE", "PURPOSE", "to have meaning and direction in my life",
     "СМЫСЛ", "иметь в жизни смысл и направление", "OUTSIDE", "low", ""),
    (80, "RATIONALITY", "RATIONALITY", "to be guided by reason, logic, and evidence",
     "РАЦИОНАЛЬНОСТЬ", "руководствоваться разумом, логикой и фактами", "SD-T", "low", ""),
    (81, "REALISM", "REALISM", "to see and act realistically and practically",
     "РЕАЛИЗМ", "смотреть на вещи реалистично и действовать практично", "OUTSIDE", "low", ""),
    (82, "RESPONSIBILITY", "RESPONSIBILITY", "to make and carry out responsible decisions",
     "ОТВЕТСТВЕННОСТЬ", "принимать ответственные решения и выполнять их", "BE-D", "high", ""),
    (83, "RISK", "RISK", "to take risks and chances",
     "РИСК", "рисковать и испытывать удачу", "ST", "high", ""),
    (84, "ROMANCE", "ROMANCE", "to have intense, exciting love in my life",
     "РОМАНТИКА", "переживать сильную, яркую любовь", "OUTSIDE", "low", "intimate"),
    (85, "SAFETY", "SAFETY", "to be safe and secure",
     "БЕЗОПАСНОСТЬ", "жить в безопасности и защищённости", "SE-P", "high", ""),
    (86, "SELF_ACCEPTANCE", "SELF-ACCEPTANCE", "to accept myself as I am",
     "САМОПРИНЯТИЕ", "принимать себя целиком, со всеми особенностями", "OUTSIDE", "low", ""),
    (87, "SELF_CONTROL", "SELF-CONTROL", "to be disciplined in my own actions",
     "САМОКОНТРОЛЬ", "дисциплинированно управлять своими поступками", "CO-R", "medium", ""),
    (88, "SELF_ESTEEM", "SELF-ESTEEM", "to feel good about myself",
     "САМОУВАЖЕНИЕ", "хорошо относиться к себе", "OUTSIDE", "low", ""),
    (89, "SELF_KNOWLEDGE", "SELF-KNOWLEDGE", "to have a deep and honest understanding of myself",
     "САМОПОЗНАНИЕ", "глубоко и честно понимать себя", "SD-T", "low", ""),
    (90, "SERVICE", "SERVICE", "to be helpful and of service to others",
     "СЛУЖЕНИЕ", "помогать другим и приносить им пользу", "BE-C", "high", ""),
    (91, "SEXUALITY", "SEXUALITY", "to have an active and satisfying sex life",
     "СЕКСУАЛЬНОСТЬ", "вести активную и приносящую удовлетворение сексуальную жизнь", "HE", "medium", "intimate"),
    (92, "SIMPLICITY", "SIMPLICITY", "to live life simply, with minimal needs",
     "ПРОСТОТА", "жить просто, с минимальными потребностями", "TR", "low", ""),
    (93, "SOLITUDE", "SOLITUDE", "to have time and space where I can be apart from others",
     "УЕДИНЕНИЕ", "иметь время и место, чтобы побыть наедине с собой", "SD-A", "low", ""),
    (94, "SPIRITUALITY", "SPIRITUALITY", "to grow and mature spiritually",
     "ДУХОВНОСТЬ", "расти и созревать духовно", "OUTSIDE", "low", ""),
    (95, "STABILITY", "STABILITY", "to have a life that stays fairly consistent",
     "СТАБИЛЬНОСТЬ", "жить достаточно постоянной и предсказуемой жизнью", "SE-P", "high", ""),
    (96, "TOLERANCE", "TOLERANCE", "to accept and respect those who differ from me",
     "ТЕРПИМОСТЬ", "принимать и уважать тех, кто отличается от меня", "UN-T", "high", ""),
    (97, "TRADITION", "TRADITION", "to follow respected patterns of the past",
     "ТРАДИЦИИ", "следовать уважаемым образцам прошлого", "TR", "high", ""),
    (98, "VIRTUE", "VIRTUE", "to live a morally pure and excellent life",
     "ДОБРОДЕТЕЛЬ", "жить нравственно чистой и достойной жизнью", "TR", "low", ""),
    (99, "WEALTH", "WEALTH", "to have plenty of money",
     "БОГАТСТВО", "иметь много денег", "PO-R", "high", ""),
    (100, "WORLD_PEACE", "WORLD PEACE", "to work to promote peace in the world",
     "МИР НА ЗЕМЛЕ", "способствовать миру во всём мире", "UN-C", "high", ""),
]

# Венгерский перевод (авторский, требует проверки носителем языка). key -> (name_hu, def_hu)
_HU = {
    "ACCEPTANCE": ("ELFOGADÁS", "hogy olyannak fogadjanak el, amilyen vagyok"),
    "ACCURACY": ("PONTOSSÁG", "hogy helyesek legyenek a véleményeim és a meggyőződéseim"),
    "ACHIEVEMENT": ("TELJESÍTMÉNY", "jelentős eredményeket elérni"),
    "ADVENTURE": ("KALAND", "új és izgalmas élményeket átélni"),
    "ART": ("MŰVÉSZET", "értékelni a művészetet, vagy kifejezni magam általa"),
    "ATTRACTIVENESS": ("VONZERŐ", "fizikailag vonzónak lenni"),
    "AUTHORITY": ("IRÁNYÍTÓ SZEREP", "mások élén állni"),
    "AUTONOMY": ("AUTONÓMIA", "önállóan és függetlenül alakítani az életemet"),
    "BEAUTY": ("SZÉPSÉG", "értékelni a körülöttem lévő szépséget"),
    "BELONGING": ("ÖSSZETARTOZÁS", "érezni, hogy valahová tartozom, valaminek a része vagyok"),
    "CARING": ("GONDOSKODÁS", "gondoskodni másokról"),
    "CHALLENGE": ("KIHÍVÁS", "nehéz feladatokat és problémákat vállalni"),
    "COMFORT": ("KÉNYELEM", "kellemes és kényelmes életet élni"),
    "COMMITMENT": ("ELKÖTELEZŐDÉS", "tartós, jelentőségteljes elköteleződéseket vállalni"),
    "COMPASSION": ("EGYÜTTÉRZÉS", "együttérezni másokkal, és ennek megfelelően cselekedni"),
    "COMPLEXITY": ("ÖSSZETETTSÉG", "elfogadni az élet bonyolultságát és sokrétűségét"),
    "COMPROMISE": ("KOMPROMISSZUM", "kész lenni engedni és kérni a megegyezés érdekében"),
    "CONTRIBUTION": ("HOZZÁJÁRULÁS", "maradandóan hozzájárulni a világhoz"),
    "COOPERATION": ("EGYÜTTMŰKÖDÉS", "másokkal együttműködve dolgozni"),
    "COURAGE": ("BÁTORSÁG", "bátornak és erősnek lenni a nehézségekkel szemben"),
    "COURTESY": ("UDVARIASSÁG", "figyelmesnek és udvariasnak lenni másokkal"),
    "CREATIVITY": ("KREATIVITÁS", "új dolgokat vagy ötleteket alkotni"),
    "CURIOSITY": ("KÍVÁNCSISÁG", "új dolgokat keresni, kipróbálni és megismerni"),
    "DEPENDABILITY": ("MEGBÍZHATÓSÁG", "megbízhatónak lenni, akire lehet számítani"),
    "DILIGENCE": ("ALAPOSSÁG", "bármit csinálok, alaposan és lelkiismeretesen csinálni"),
    "DUTY": ("KÖTELESSÉG", "teljesíteni a kötelességeimet és a vállalásaimat"),
    "ECOLOGY": ("ÖKOLÓGIA", "harmóniában élni a természettel"),
    "EXCITEMENT": ("IZGALOM", "izgalmakkal és erős élményekkel teli életet élni"),
    "FAITHFULNESS": ("HŰSÉG", "hűségesnek és lojálisnak lenni a kapcsolataimban"),
    "FAME": ("HÍRNÉV", "ismertnek és elismertnek lenni"),
    "FAMILY": ("CSALÁD", "boldog, szerető családban élni"),
    "FITNESS": ("ERŐNLÉT", "fizikailag erősnek és jó formában lenni"),
    "FLEXIBILITY": ("RUGALMASSÁG", "könnyen alkalmazkodni az új helyzetekhez"),
    "FORGIVENESS": ("MEGBOCSÁTÁS", "megbocsátani másoknak"),
    "FREEDOM": ("SZABADSÁG", "mentesnek lenni a fölösleges korlátozásoktól"),
    "FRIENDSHIP": ("BARÁTSÁG", "hogy legyenek közeli barátaim, akikre támaszkodhatok"),
    "FUN": ("SZÓRAKOZÁS", "játszani és jól szórakozni"),
    "GENEROSITY": ("NAGYLELKŰSÉG", "megosztani másokkal azt, amim van"),
    "GENUINENESS": ("HITELESSÉG", "önmagamhoz hűen cselekedni"),
    "GODS_WILL": ("ISTEN AKARATA", "keresni Isten akaratát, és követni azt"),
    "GRATITUDE": ("HÁLA", "hálásnak lenni, és kifejezni a megbecsülésemet"),
    "GROWTH": ("FEJLŐDÉS", "folyamatosan változni és fejlődni"),
    "HEALTH": ("EGÉSZSÉG", "testileg jól lenni és egészségesnek maradni"),
    "HONESTY": ("ŐSZINTESÉG", "őszintének és igazmondónak lenni"),
    "HOPE": ("REMÉNY", "megőrizni a pozitív, derűlátó szemléletet"),
    "HUMILITY": ("SZERÉNYSÉG", "szerénynek lenni, nem tolakodni az előtérbe"),
    "HUMOR": ("HUMOR", "meglátni a humoros oldalát önmagamnak és a világnak"),
    "IMAGINATION": ("KÉPZELET", "álmodni és meglátni a lehetőségeket"),
    "INDEPENDENCE": ("FÜGGETLENSÉG", "nem függeni másoktól"),
    "INDUSTRY": ("SZORGALOM", "keményen és jól dolgozni az életfeladataimon"),
    "INNER_PEACE": ("BELSŐ BÉKE", "megélni a lelki békét"),
    "INTEGRITY": ("INTEGRITÁS", "a mindennapjaimat az értékeimmel összhangban élni"),
    "INTELLIGENCE": ("SZELLEMI FRISSESSÉG", "élesen és aktívan tartani az elmémet"),
    "INTIMACY": ("INTIMITÁS", "megosztani másokkal a legbensőbb élményeimet"),
    "JUSTICE": ("IGAZSÁGOSSÁG", "kiállni mindenki tisztességes és egyenlő kezeléséért"),
    "KNOWLEDGE": ("TUDÁS", "tanulni, és értékes tudással hozzájárulni"),
    "LEADERSHIP": ("VEZETÉS", "inspirálni és irányítani másokat"),
    "LEISURE": ("PIHENÉS", "időt szakítani a kikapcsolódásra és az élvezetekre"),
    "LOVED": ("SZERETVE LENNI", "hogy szeressenek azok, akik közel állnak hozzám"),
    "LOVING": ("SZERETNI", "szeretetet adni másoknak"),
    "MASTERY": ("HOZZÁÉRTÉS", "rátermettnek lenni a mindennapi tevékenységeimben"),
    "MINDFULNESS": ("TUDATOS JELENLÉT", "tudatosan, a jelen pillanatban élni"),
    "MODERATION": ("MÉRTÉKLETESSÉG", "kerülni a végleteket, és megtalálni az arany középutat"),
    "MONOGAMY": ("MONOGÁMIA", "egyetlen közeli, szeretetteljes kapcsolatban élni"),
    "MUSIC": ("ZENE", "élvezni a zenét, vagy kifejezni magam általa"),
    "NON_CONFORMITY": ("NONKONFORMIZMUS", "megkérdőjelezni és kihívni a tekintélyt és a normákat"),
    "NOVELTY": ("ÚJDONSÁG", "változásokkal és változatossággal teli életet élni"),
    "NURTURANCE": ("TÁMOGATÁS", "bátorítani és támogatni másokat"),
    "OPENNESS": ("NYITOTTSÁG", "nyitottnak lenni az új élményekre, ötletekre és lehetőségekre"),
    "ORDER": ("REND", "rendezett és szervezett életet élni"),
    "PASSION": ("SZENVEDÉLY", "mély érzéseket táplálni eszmék, tevékenységek vagy emberek iránt"),
    "PATRIOTISM": ("HAZASZERETET", "szeretni, szolgálni és védeni a hazámat"),
    "PLEASURE": ("ÉLVEZET", "jó érzéseket átélni"),
    "POPULARITY": ("NÉPSZERŰSÉG", "hogy sokan kedveljenek"),
    "POWER": ("HATALOM", "irányítást gyakorolni mások felett"),
    "PRACTICALITY": ("GYAKORLATIASSÁG", "arra összpontosítani, ami gyakorlatias, körültekintő és észszerű"),
    "PROTECT": ("VÉDELMEZÉS", "megvédeni és biztonságban tudni azokat, akiket szeretek"),
    "PROVIDE": ("A CSALÁD ELTARTÁSA", "eltartani a családomat és gondoskodni róla"),
    "PURPOSE": ("ÉLETCÉL", "hogy az életemnek értelme és iránya legyen"),
    "RATIONALITY": ("RACIONALITÁS", "az észszerűség, a logika és a tények alapján dönteni"),
    "REALISM": ("REALIZMUS", "reálisan látni a dolgokat, és gyakorlatiasan cselekedni"),
    "RESPONSIBILITY": ("FELELŐSSÉG", "felelős döntéseket hozni és végrehajtani"),
    "RISK": ("KOCKÁZAT", "kockázatot vállalni, és élni a lehetőségekkel"),
    "ROMANCE": ("ROMANTIKA", "intenzív, izgalmas szerelmet megélni"),
    "SAFETY": ("BIZTONSÁG", "biztonságban és védettségben élni"),
    "SELF_ACCEPTANCE": ("ÖNELFOGADÁS", "elfogadni magam olyannak, amilyen vagyok"),
    "SELF_CONTROL": ("ÖNFEGYELEM", "fegyelmezetten irányítani a tetteimet"),
    "SELF_ESTEEM": ("ÖNBECSÜLÉS", "elégedettnek lenni önmagammal"),
    "SELF_KNOWLEDGE": ("ÖNISMERET", "mélyen és őszintén ismerni önmagam"),
    "SERVICE": ("SZOLGÁLAT", "segítőkésznek lenni, és mások szolgálatára állni"),
    "SEXUALITY": ("SZEXUALITÁS", "aktív és kielégítő szexuális életet élni"),
    "SIMPLICITY": ("EGYSZERŰSÉG", "egyszerűen, kevés igénnyel élni"),
    "SOLITUDE": ("EGYEDÜLLÉT", "időt és teret találni arra, hogy egyedül lehessek"),
    "SPIRITUALITY": ("SPIRITUALITÁS", "lelkileg növekedni és érni"),
    "STABILITY": ("STABILITÁS", "viszonylag állandó, kiszámítható életet élni"),
    "TOLERANCE": ("TOLERANCIA", "elfogadni és tisztelni azokat, akik különböznek tőlem"),
    "TRADITION": ("HAGYOMÁNY", "követni a múlt tiszteletre méltó mintáit"),
    "VIRTUE": ("ERÉNY", "erkölcsileg tiszta és kiváló életet élni"),
    "WEALTH": ("GAZDAGSÁG", "sok pénzzel rendelkezni"),
    "WORLD_PEACE": ("VILÁGBÉKE", "tenni a világbéke előmozdításáért"),
}

_FIELDS = ("id", "key", "name_en", "def_en", "name_ru", "def_ru",
           "schwartz", "confidence", "sensitive")
LANGS = ("en", "ru", "hu")

CARDS = [dict(zip(_FIELDS, row)) for row in _ROWS]
for _c in CARDS:
    _c["higher_order"] = SCHWARTZ_19[_c["schwartz"]][2]
    _c["name_hu"], _c["def_hu"] = _HU[_c["key"]]

CARDS_BY_KEY = {c["key"]: c for c in CARDS}


def schwartz_mapping() -> dict:
    """{код Шварца: [ключи карточек]} — генерируется из набора, а не пишется руками."""
    mapping = {code: [] for code in SCHWARTZ_19}
    for c in CARDS:
        mapping[c["schwartz"]].append(c["key"])
    return mapping


def validate() -> None:
    assert len(CARDS) == 100, len(CARDS)
    assert [c["id"] for c in CARDS] == list(range(1, 101)), "ids must be 1..100 in order"
    assert len(CARDS_BY_KEY) == 100, "duplicate keys"
    assert set(_HU) == set(CARDS_BY_KEY), "HU keys mismatch"
    for lang in LANGS:
        names = [c[f"name_{lang}"] for c in CARDS]
        assert len(set(names)) == 100, f"duplicate {lang} names"
        assert all(c[f"name_{lang}"].strip() and c[f"def_{lang}"].strip() for c in CARDS), lang
    for c in CARDS:
        assert c["schwartz"] in SCHWARTZ_19, c
        assert c["confidence"] in {"high", "medium", "low"}, c
        assert c["sensitive"] in {"", "religion", "intimate", "political"}, c


if __name__ == "__main__":
    validate()
    out = Path(__file__).with_name("value_cards_100.csv")
    with out.open("w", newline="", encoding="utf-8-sig") as f:  # utf-8-sig: Excel корректно открывает кириллицу
        w = csv.DictWriter(f, fieldnames=list(_FIELDS) + ["name_hu", "def_hu", "higher_order"])
        w.writeheader()
        w.writerows(CARDS)

    print(f"OK: {len(CARDS)} cards -> {out.name}")
    print("\nКарточек на ценность Шварца:")
    for code, keys in schwartz_mapping().items():
        print(f"  {code:8s} {SCHWARTZ_19[code][1]:32s} {len(keys):3d}")
    print("\nПо полюсам:", dict(Counter(c["higher_order"] for c in CARDS)))
    print("Уверенность привязки:", dict(Counter(c["confidence"] for c in CARDS)))
    print("Чувствительные:", [c["key"] for c in CARDS if c["sensitive"]])
