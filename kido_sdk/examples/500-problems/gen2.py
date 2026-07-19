import os, sys

BASE = (
    r"C:\Users\anime\OneDrive\Desktop\Kidcode\KideCOde\kido_sdk\examples\500-problems"
)


def w(d, f, c):
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f)
    if not os.path.exists(p):
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(c.strip() + "\n")
        return True
    return False


# ---- 12-drawing-music ----
d12 = os.path.join(BASE, "12-drawing-music")
progs = [
    (
        "dr001",
        "Drawing: Smiley face with characters",
        'print "  *****"\nprint " *     *"\nprint "*  O O  *"\nprint "*   ^   *"\nprint "*  \\_/ *"\nprint " *     *"\nprint "  *****"\nprint "A happy smiley face!"',
    ),
    (
        "dr002",
        "Drawing: House using characters",
        'print "   /\\\\"\nprint "  /  \\\\"\nprint " /    \\\\"\nprint "/______\\\\"\nprint "|      |"\nprint "|  []  |"\nprint "|______|"\nprint "A cozy house!"',
    ),
    (
        "dr003",
        "Drawing: Christmas tree with stars",
        'print "   *"\nprint "  ***"\nprint " *****"\nprint "*******"\nprint "  |||"\nprint "  |||"\nprint "Merry Christmas!"',
    ),
    (
        "dr004",
        "Drawing: Rocket ship",
        'print "   /\\\\"\nprint "  /  \\\\"\nprint " /    \\\\"\nprint " |    |"\nprint " |    |"\nprint " |    |"\nprint " /\\\\/\\\\"\nprint "/______\\\\"\nprint "3... 2... 1... Blast off!"',
    ),
    (
        "dr005",
        "Drawing: Rainbow colors",
        'print "R - Red"\nprint "  O - Orange"\nprint "    Y - Yellow"\nprint "      G - Green"\nprint "        B - Blue"\nprint "          I - Indigo"\nprint "            V - Violet"\nprint "ROYGBIV - Rainbow colors!"',
    ),
    (
        "dr006",
        "Drawing: Cute cat",
        'print "  /\\\\___/\\\\"\nprint " (  o o  )"\nprint " (  =^=  )"\nprint "  |     |"\nprint "  |     |"\nprint "  |_____|"\nprint "Meow!"',
    ),
    (
        "dr007",
        "Music: Musical scale notes",
        'list notes = "Do" "Re" "Mi" "Fa" "So" "La" "Ti" "Do"\nprint "Major Scale:"\nrepeat length notes times as i\n    print notes at i\nprint "Do Re Mi Fa So La Ti Do!"',
    ),
    (
        "dr008",
        "Music: Rhythm pattern",
        'list pattern = "beat" "rest" "beat" "beat" "rest"\nprint "Clap along:"\nrepeat length pattern times as i\n    print i "." pattern at i',
    ),
    (
        "dr009",
        "Drawing: Ice cream cone",
        'print "   /\\\\"\nprint "  /  \\\\"\nprint " | () |"\nprint " | () |"\nprint " | () |"\nprint "  \\\\/"\nprint "   |||"\nprint "Yummy ice cream!"',
    ),
]
for f, title, content in progs:
    full = f"# {title}\n{content}"
    if w(d12, f + ".kd", full):
        print(f"Created: 12/{f}")

# ---- 13-calendar-time ----
d13 = os.path.join(BASE, "13-calendar-time")
progs = [
    (
        "tm001",
        "Calendar: Days in each month",
        'remember m = 7\nif m is 1 or m is 3 or m is 5 or m is 7 or m is 8 or m is 10 or m is 12\n    print "Month" m "has 31 days"\nelse if m is 4 or m is 6 or m is 9 or m is 11\n    print "Month" m "has 30 days"\nelse if m is 2\n    print "February has 28 days (29 in leap year)"',
    ),
    (
        "tm002",
        "Calendar: Day of week finder",
        'remember d = 3\nlist days = "Monday" "Tuesday" "Wednesday" "Thursday" "Friday" "Saturday" "Sunday"\nprint "Day" d "is" days at d',
    ),
    (
        "tm003",
        "Calendar: Season by month",
        'remember m = 7\nif m is 12 or m is 1 or m is 2\n    print "Winter"\nelse if m is 3 or m is 4 or m is 5\n    print "Spring"\nelse if m is 6 or m is 7 or m is 8\n    print "Summer"\nelse\n    print "Fall"',
    ),
    (
        "tm004",
        "Calendar: Birthday countdown",
        'remember bday = 25\nremember today = 18\nremember left = bday - today\nif left bigger 0\n    print left "days until your birthday!"\nelse\n    print "Happy Birthday!"',
    ),
    (
        "tm005",
        "Time: Minutes to hours",
        'remember total = 130\nremember h = total / 60\nremember m = total - h * 60\nprint total "minutes =" h "hours" m "minutes"',
    ),
    (
        "tm006",
        "Time: Seconds to minutes",
        'remember total = 200\nremember m = total / 60\nremember s = total - m * 60\nprint total "seconds =" m "minutes" s "seconds"',
    ),
    (
        "tm007",
        "Time: Hours to days",
        'remember total = 50\nremember d = total / 24\nremember h = total - d * 24\nprint total "hours =" d "days" h "hours"',
    ),
    (
        "tm008",
        "Calendar: After this month",
        'remember m = 7\nlist months = "Jan" "Feb" "Mar" "Apr" "May" "Jun" "Jul" "Aug" "Sep" "Oct" "Nov" "Dec"\nif m smaller 12\n    print "After" months at m "comes" months at m + 1\nelse\n    print "After December comes January"',
    ),
    (
        "tm009",
        "Time: Hours in a week",
        'remember hours = 24 * 7\nprint "There are" hours "hours in a week"',
    ),
    (
        "tm010",
        "Calendar: Weekend checker",
        'remember day = "Saturday"\nif day is "Saturday" or day is "Sunday"\n    print day "is a weekend! Time to play!"\nelse\n    print day "is a weekday. School day!"',
    ),
    (
        "tm011",
        "Time: Age in months",
        'remember years = 10\nremember months = years * 12\nprint "Age" years "years =" months "months old"',
    ),
    (
        "tm012",
        "Calendar: Months with 31 days",
        'list months31 = "Jan" "Mar" "May" "Jul" "Aug" "Oct" "Dec"\nprint "Months with 31 days:"\nrepeat length months31 times as i\n    print months31 at i',
    ),
    (
        "tm013",
        "Time: Minutes in an hour",
        'remember mins = 60\nprint "1 hour =" mins "minutes"\nremember in_day = mins * 24\nprint "1 day =" in_day "minutes"',
    ),
    (
        "tm014",
        "Calendar: Birth season finder",
        'remember month = 7\nif month bigger or same 3 and month smaller or same 5\n    print "Born in Spring!"\nelse if month bigger or same 6 and month smaller or same 8\n    print "Born in Summer!"\nelse if month bigger or same 9 and month smaller or same 11\n    print "Born in Fall!"\nelse\n    print "Born in Winter!"',
    ),
    (
        "tm015",
        "Time: Seconds to HH:MM:SS",
        'remember total = 3665\nremember h = total / 3600\nremember r = total - h * 3600\nremember m = r / 60\nremember s = r - m * 60\nprint total "seconds =" h ":" m ":" s',
    ),
]
for f, title, content in progs:
    full = f"# {title}\n{content}"
    if w(d13, f + ".kd", full):
        print(f"Created: 13/{f}")

# ---- 14-geometry ----
d14 = os.path.join(BASE, "14-geometry")
progs = [
    (
        "geo001",
        "Geometry: Area of a rectangle",
        'remember w = 5\nremember h = 3\nremember area = w * h\nprint "Rectangle " w "x" h "area =" area',
    ),
    (
        "geo002",
        "Geometry: Area of a triangle",
        'remember base = 6\nremember height = 4\nremember area = base * height / 2\nprint "Triangle area =" area',
    ),
    (
        "geo003",
        "Geometry: Perimeter of a rectangle",
        'remember w = 5\nremember h = 3\nremember p = 2 * (w + h)\nprint "Perimeter =" p',
    ),
    (
        "geo004",
        "Geometry: Circumference of a circle",
        'remember r = 7\nconst pi = 3.14159\nremember c = 2 * pi * r\nprint "Circumference =" c',
    ),
    (
        "geo005",
        "Geometry: Volume of a cube",
        'remember side = 4\nremember vol = side * side * side\nprint "Cube volume =" vol',
    ),
    (
        "geo006",
        "Geometry: Surface area of a box",
        'remember l = 4\nremember w = 3\nremember h = 2\nremember sa = 2 * (l * w + l * h + w * h)\nprint "Surface area =" sa',
    ),
    (
        "geo007",
        "Geometry: Pythagorean theorem",
        'remember a = 3\nremember b = 4\nremember c_sq = a * a + b * b\nprint "If a=" a "and b=" b\nprint "Then c^2 =" c_sq\nprint "So c =" sqrt c_sq',
    ),
    (
        "geo008",
        "Geometry: Area of a square",
        'remember side = 5\nremember area = side * side\nprint "Square area =" area',
    ),
    (
        "geo009",
        "Geometry: Volume of a box",
        'remember l = 5\nremember w = 3\nremember h = 4\nremember vol = l * w * h\nprint "Box volume =" vol',
    ),
    (
        "geo010",
        "Measurement: Inches to centimeters",
        'remember inches = 12\nremember cm = inches * 2.54\nprint inches "inches =" cm "cm"',
    ),
    (
        "geo011",
        "Measurement: Feet to meters",
        'remember feet = 10\nremember meters = feet * 0.3048\nprint feet "feet =" meters "meters"',
    ),
    (
        "geo012",
        "Measurement: Kilometers to miles",
        'remember km = 10\nremember miles = km * 0.621371\nprint km "km =" miles "miles"',
    ),
    (
        "geo013",
        "Geometry: Perimeter of a triangle",
        'remember a = 3\nremember b = 4\nremember c = 5\nremember p = a + b + c\nprint "Triangle perimeter =" p',
    ),
    (
        "geo014",
        "Measurement: Liters to cups",
        'remember liters = 2\nremember cups = liters * 4.22675\nprint liters "liters =" cups "cups"',
    ),
    (
        "geo015",
        "Measurement: Kilograms to pounds",
        'remember kg = 5\nremember lb = kg * 2.20462\nprint kg "kg =" lb "lbs"',
    ),
    (
        "geo016",
        "Geometry: Area of a circle",
        'remember r = 5\nconst pi = 3.14159\nremember area = pi * r * r\nprint "Circle area =" area',
    ),
    (
        "geo017",
        "Measurement: Celsius to Fahrenheit",
        'remember c = 25\nremember f = c * 9 / 5 + 32\nprint c "C =" f "F"',
    ),
    (
        "geo018",
        "Measurement: Miles per gallon to km per liter",
        'remember mpg = 30\nremember kmpl = mpg * 0.425144\nprint mpg "MPG =" kmpl "km/L"',
    ),
    (
        "geo019",
        "Geometry: Volume of a cylinder",
        'remember r = 3\nremember h = 5\nconst pi = 3.14159\nremember vol = pi * r * r * h\nprint "Cylinder volume =" vol',
    ),
    (
        "geo020",
        "Geometry: Diagonal of a rectangle",
        'remember w = 3\nremember h = 4\nremember diag_sq = w * w + h * h\nremember diag = sqrt diag_sq\nprint "Rectangle diagonal =" diag',
    ),
]
for f, title, content in progs:
    full = f"# {title}\n{content}"
    if w(d14, f + ".kd", full):
        print(f"Created: 14/{f}")

# ---- 15-crypto ----
d15 = os.path.join(BASE, "15-crypto")
progs = [
    (
        "cr001",
        "Crypto: Caesar cipher",
        'remember text = "hello"\nprint "Original:" text\nprint "Shift by 3:"\nprint "khoor (hello shifted by 3)"',
    ),
    (
        "cr002",
        "Crypto: Atbash cipher",
        'remember text = "hello"\nprint "Original:" text\nprint "Atbash: svool (a->z, b->y, etc)"',
    ),
    (
        "cr003",
        "Crypto: Number substitution",
        'remember word = "abc"\nprint "Word:" word\nprint "Numbers: 1 2 3 (a=1, b=2, c=3)"',
    ),
    (
        "cr004",
        "Crypto: Reverse cipher",
        'remember text = "kido"\nprint "Original:" text\nprint "Reversed:"\nremember n = length text\nrepeat n times as i\n    print text at (n - i + 1)',
    ),
    (
        "cr005",
        "Crypto: Vowel replacement",
        'remember text = "hello world"\nprint "Original:" text\nremember encoded = replace text "e" "3"\nremember encoded = replace encoded "o" "0"\nprint "Encoded:" encoded',
    ),
    (
        "cr006",
        "Crypto: Letter pair swap",
        'print "Original: secret"\nprint "Swapped pairs: a<->b, c<->d, etc"\nprint "Result: tfcqes"',
    ),
    (
        "cr007",
        "Crypto: Keyboard shift",
        'print "Original: hello"\nprint "Shift right on QWERTY:"\nprint "h->j, e->r, l->., l->., o->p"\nprint "Result: jr..p"',
    ),
    ("cr008", "Crypto: Morse code", 'print "SOS in Morse:"\nprint "... --- ..."'),
    (
        "cr009",
        "Crypto: Emoji cipher",
        'print "Cipher: a=smile, b=heart, c=star"\nprint "abc -> smile heart star"',
    ),
    (
        "cr010",
        "Crypto: Pigpen cipher",
        'list pairs = "ab" "cd" "ef"\nprint "Pigpen: swap each letter with its pair"\nprint "hello -> ifkks"',
    ),
]
for f, title, content in progs:
    full = f"# {title}\n{content}"
    if w(d15, f + ".kd", full):
        print(f"Created: 15/{f}")

# ---- 16-probability-stats ----
d16 = os.path.join(BASE, "16-probability-stats")
progs = [
    (
        "st001",
        "Stats: Coin flips",
        'remember heads = 0\nremember tails = 0\nrepeat 100 times as i\n    remember flip = random 1 2\n    if flip is 1\n        remember heads = heads + 1\n    else\n        remember tails = tails + 1\nprint "100 coin flips:"\nprint "Heads:" heads\nprint "Tails:" tails"',
    ),
    (
        "st002",
        "Stats: Dice rolls",
        'remember ones = 0\nremember twos = 0\nremember threes = 0\nremember fours = 0\nremember fives = 0\nremember sixes = 0\nrepeat 60 times as i\n    remember roll = random 1 6\n    if roll is 1\n        remember ones = ones + 1\n    elif roll is 2\n        remember twos = twos + 1\n    elif roll is 3\n        remember threes = threes + 1\n    elif roll is 4\n        remember fours = fours + 1\n    elif roll is 5\n        remember fives = fives + 1\n    else\n        remember sixes = sixes + 1\nprint "Dice roll distribution:"\nprint "1:" ones "2:" twos "3:" threes"',
    ),
    (
        "st003",
        "Stats: Average of 100 rolls",
        'remember sum = 0\nrepeat 100 times as i\n    remember roll = random 1 6\n    remember sum = sum + roll\nremember avg = sum / 100\nprint "Average of 100 dice rolls:" avg"',
    ),
    (
        "st004",
        "Stats: Double sixes probability",
        'remember double_six = 0\nrepeat 1000 times as i\n    remember d1 = random 1 6\n    remember d2 = random 1 6\n    if d1 is 6 and d2 is 6\n        remember double_six = double_six + 1\nprint "Double sixes in 1000 rolls:" double_six"',
    ),
    (
        "st005",
        "Stats: Even vs odd",
        'remember evens = 0\nremember odds = 0\nrepeat 100 times as i\n    remember num = random 1 100\n    if num % 2 is 0\n        remember evens = evens + 1\n    else\n        remember odds = odds + 1\nprint "Even:" evens "Odd:" odds"',
    ),
    (
        "st006",
        "Stats: Histogram",
        'list counts = 0 0 0 0 0 0 0 0 0 0\nrepeat 100 times as i\n    remember num = random 1 10\n    if num is 1  counts at 1 = counts at 1 + 1\n    elif num is 2  counts at 2 = counts at 2 + 1\n    elif num is 3  counts at 3 = counts at 3 + 1\n    elif num is 4  counts at 4 = counts at 4 + 1\n    elif num is 5  counts at 5 = counts at 5 + 1\n    elif num is 6  counts at 6 = counts at 6 + 1\n    elif num is 7  counts at 7 = counts at 7 + 1\n    elif num is 8  counts at 8 = counts at 8 + 1\n    elif num is 9  counts at 9 = counts at 9 + 1\n    elif num is 10  counts at 10 = counts at 10 + 1\nprint "Histogram:"\nrepeat 10 times as i\n    print i ":" counts at i"',
    ),
]
for f, title, content in progs:
    full = f"# {title}\n{content}"
    if w(d16, f + ".kd", full):
        print(f"Created: 16/{f}")

# ---- 17-education-school ----
d17 = os.path.join(BASE, "17-education-school")
progs = [
    (
        "ed001",
        "School: Times table",
        'remember num = 7\nprint "Multiplication Table for" num":"\nrepeat 10 times as i\n    print num "x" i "=" num * i',
    ),
    (
        "ed002",
        "School: Spelling practice",
        'remember word = "butterfly"\nprint "Spell: " word\nlist chars = "b" "u" "t" "t" "e" "r" "f" "l" "y"\nshuffle chars\nprint "Scrambled:"\njoin chars " "\nprint join chars " "',
    ),
    (
        "ed003",
        "School: Calculator",
        'remember a = 15\nremember b = 4\nprint "Calculator:"\nprint a "+" b "=" a + b\nprint a "-" b "=" a - b\nprint a "*" b "=" a * b',
    ),
    (
        "ed004",
        "School: Fraction to decimal",
        'remember num = 3\nremember den = 4\nremember decimal = num / den\nprint num "/" den "=" decimal',
    ),
    (
        "ed005",
        "School: Grade tracker",
        'remember math = 92\nremember eng = 88\nremember sci = 95\nremember total = math + eng + sci\nremember avg = total / 3\nprint "Average grade:" avg',
    ),
    (
        "ed006",
        "School: Count vowels",
        'remember word = "education"\nlist vowels = "a" "e" "i" "o" "u"\nremember count = 0\nrepeat length word times as i\n    if has vowels word at i\n        remember count = count + 1\nprint "Vowels in" word ":" count',
    ),
    (
        "ed007",
        "School: Roman numerals",
        'print "Number 7 = VII"\nprint "Number 9 = IX"\nprint "Number 42 = XLII"',
    ),
    (
        "ed008",
        "School: Homework planner",
        'remember subjects = 4\nremember mins = 30\nremember total = subjects * mins\nprint "Homework time:" total "minutes"',
    ),
    (
        "ed009",
        "School: Class schedule",
        'list days = "Mon" "Tue" "Wed" "Thu" "Fri"\nlist subs = "Math" "English" "Science" "History" "Art"\nprint "Schedule:"\nrepeat 5 times as i\n    print days at i ":" subs at i',
    ),
    (
        "ed010",
        "School: Reading speed",
        'remember words = 200\nremember mins = 4\nremember speed = words / mins\nprint "Reading:" speed "words/min"',
    ),
    (
        "ed011",
        "School: Alphabet",
        'list letters = "a" "b" "c" "d" "e" "f" "g" "h" "i" "j" "k" "l" "m" "n" "o" "p" "q" "r" "s" "t" "u" "v" "w" "x" "y" "z"\nprint "Alphabet has" length letters "letters"',
    ),
    (
        "ed012",
        "School: Quiz score analyzer",
        'list scores = 95 87 78 92 88\nsort scores\nremember total = 0\nrepeat length scores times as i\n    remember total = total + scores at i\nprint "High:" scores at length scores "Low:" scores at 1 "Avg:" total / length scores',
    ),
    (
        "ed013",
        "School: Practice timer",
        'remember t = 10\nprint "Countdown:"\nrepeat t times as i\n    print t - i + 1\nprint "Go!"',
    ),
    (
        "ed014",
        "School: Points reward",
        'remember pts = 0\nremember pts = pts + 10\nprint "Homework done! +10. Total:" pts\nremember pts = pts + 5\nprint "Helped friend! +5. Total:" pts',
    ),
    (
        "ed015",
        "School: Study plan",
        'remember days = 5\nremember hours = 2\nprint "Study" days "days x" hours "hrs =" days * hours "total hours"',
    ),
]
for f, title, content in progs:
    full = f"# {title}\n{content}"
    if w(d17, f + ".kd", full):
        print(f"Created: 17/{f}")

# ---- 18-life-skills ----
d18 = os.path.join(BASE, "18-life-skills")
progs = [
    (
        "sk001",
        "Life: Allowance",
        'remember allow = 10\nremember spent = 4\nremember saved = 3\nprint "Allowance: $" allow "Spent: $" spent "Saved: $" saved"',
    ),
    (
        "sk002",
        "Life: Chore checklist",
        'list chores = "make bed" "brush teeth" "clean room" "homework"\nprint "Done:" length chores "chores!"',
    ),
    (
        "sk003",
        "Life: Water tracker",
        'remember goal = 8\nremember drank = 6\nprint "Water: " drank "/" goal "glasses"\nif drank bigger or same goal\n    print "Goal met!"\nelse\n    print goal - drank "more needed"',
    ),
    (
        "sk004",
        "Life: Reading log",
        'remember books = 5\nremember pages = 340\nprint "Read" books "books, " pages "pages"\nprint "Avg:" pages / books "pages/book"',
    ),
    (
        "sk005",
        "Life: Sleep tracker",
        'remember hours = 8\nprint "Slept" hours "hours"\nif hours smaller 8\n    print "Try to sleep more!"\nelse\n    print "Great sleep!"',
    ),
    (
        "sk006",
        "Life: Screen time",
        'remember time = 45\nremember limit = 60\nprint "Screen:" time "min (limit:" limit ")"\nif time bigger limit\n    print "Over limit! Break time!"\nelse\n    print limit - time "min remaining"',
    ),
    (
        "sk007",
        "Life: Savings goal",
        'remember goal = 100\nremember saved = 35\nprint "Saved $" saved "of $" goal "goal"\nprint goal - saved "more needed"',
    ),
    (
        "sk008",
        "Life: Morning routine",
        'list steps = "wake" "dress" "eat" "brush" "pack"\nprint "Morning routine:"\nrepeat length steps times as i\n    print i "." steps at i',
    ),
    (
        "sk009",
        "Life: Weather prep",
        'remember t = 15\nprint "Temp:" t "C"\nif t bigger 30 print "Very hot!"\nelif t bigger 20 print "Warm!"\nelif t bigger 10 print "Cool! Jacket"\nelse print "Cold! Coat!"',
    ),
    (
        "sk010",
        "Life: Pet care",
        'list tasks = "feed" "water" "walk" "play" "brush"\nprint "Pet care:"\nrepeat length tasks times as i\n    print i "." tasks at i',
    ),
    (
        "sk011",
        "Life: Party budget",
        'remember budget = 50\nremember cake = 15\nremember ballon = 5\nremember gifts = 25\nremember total = cake + ballon + gifts\nprint "Party: $" total "of $" budget "budget"\nprint "Left: $" budget - total',
    ),
    (
        "sk012",
        "Life: Room cleaning",
        'list tasks = "bed" "toys" "desk" "floor" "shelves"\nprint "Clean:"\nrepeat length tasks times as i\n    print i "." tasks at i "- done!"',
    ),
    (
        "sk013",
        "Life: Good deeds",
        'remember d = 0\nremember d = d + 1\nprint "Helped clean! Deeds:" d\nremember d = d + 1\nprint "Shared snack! Deeds:" d\nremember d = d + 1\nprint "Was kind! Deeds:" d',
    ),
    (
        "sk014",
        "Life: Healthy eating",
        'remember fruits = 3\nremember veggies = 2\nremember total = fruits + veggies\nprint "Fruits+" fruits "Veggies+" veggies "=" total "servings"\nif total bigger or same 5\n    print "5 a day goal met!"',
    ),
    (
        "sk015",
        "Life: Weekly activities",
        'list days = "Mon" "Tue" "Wed" "Thu" "Fri" "Sat" "Sun"\nlist acts = "soccer" "piano" "swim" "art" "read" "play" "family"\nprint "My Week:"\nrepeat 7 times as i\n    print days at i ":" acts at i',
    ),
]
for f, title, content in progs:
    full = f"# {title}\n{content}"
    if w(d18, f + ".kd", full):
        print(f"Created: 18/{f}")

# ---- 19-recursion ----
d19 = os.path.join(BASE, "19-recursion")
progs = [
    (
        "rc001",
        "Recursion: Factorial",
        'fun factorial n\n    if n smaller or same 1\n        return 1\n    else\n        return n * factorial(n - 1)\nremember result = factorial(5)\nprint "5! =" result',
    ),
    (
        "rc002",
        "Recursion: Fibonacci",
        'fun fib n\n    if n is 1\n        return 0\n    else if n is 2\n        return 1\n    else\n        return fib(n - 1) + fib(n - 2)\nprint "fib(10) =" fib(10)',
    ),
    (
        "rc003",
        "Recursion: Countdown",
        'fun cd n\n    if n smaller 1\n        print "Blast off!"\n        return nothing\n    else\n        print n\n        return cd(n - 1)\ncd(5)',
    ),
    (
        "rc004",
        "Recursion: Sum of N",
        'fun sum_n n\n    if n is 1\n        return 1\n    else\n        return n + sum_n(n - 1)\nprint "Sum 1-10 =" sum_n(10)',
    ),
    (
        "rc005",
        "Recursion: Power",
        'fun power b e\n    if e is 0\n        return 1\n    else\n        return b * power(b, e - 1)\nprint "2^10 =" power(2, 10)',
    ),
    (
        "rc006",
        "Recursion: Palindrome check",
        'fun is_pal s\n    if length s smaller or same 1\n        return yes\n    else if s at 1 is s at length s\n        return yes\n    else\n        return no\nif is_pal("racecar") is yes\n    print "racecar is a palindrome"\nelse\n    print "not a palindrome"',
    ),
    (
        "rc007",
        "Recursion: Tower of Hanoi",
        'fun hanoi n f t v\n    if n is 1\n        print "Move disk 1 from" f "to" t\n    else\n        hanoi(n - 1, f, v)\n        print "Move disk" n "from" f "to" t\n        hanoi(n - 1, v, t)\nprint "Tower of Hanoi (3 disks):"\nhanoi(3, "A", "C", "B")',
    ),
    (
        "rc008",
        "Recursion: Binary search",
        'list items = 1 3 5 7 9 11 13 15 17 19\nfun bsearch arr t l r\n    if l bigger r\n        return 0\n    remember mid = (l + r) / 2\n    if arr at mid is t\n        return mid\n    else if arr at mid bigger t\n        return bsearch(arr, t, l, mid - 1)\n    else\n        return bsearch(arr, t, mid + 1, r)\nprint "Searching for 7:"\nprint "Position:" bsearch(items, 7, 1, length items)',
    ),
    (
        "rc009",
        "Recursion: Count occurrences",
        'fun count_occur lst val idx\n    if idx bigger length lst\n        return 0\n    else if lst at idx is val\n        return 1 + count_occur(lst, val, idx + 1)\n    else\n        return count_occur(lst, val, idx + 1)\nlist data = 1 2 2 3 2 4\nprint "2 appears" count_occur(data, 2, 1) "times"',
    ),
    (
        "rc010",
        "Recursion: String reverse",
        'fun rev s\n    if length s is 1\n        return s\n    else\n        return rev(s from 2 to length s) + (s at 1)\nprint "Reverse of hello:"\nremember text = "hello"\nremember n = length text\nrepeat n times as i\n    print text at (n - i + 1)',
    ),
]
for f, title, content in progs:
    full = f"# {title}\n{content}"
    if w(d19, f + ".kd", full):
        print(f"Created: 19/{f}")

# ---- 20-science-nature ----
d20 = os.path.join(BASE, "20-science-nature")
progs = [
    (
        "sc001",
        "Science: Solar system",
        'dict planets = {"mercury": "smallest planet"}\nset planets "venus" "hottest planet"\nset planets "earth" "our home"\nset planets "mars" "red planet"\nset planets "jupiter" "largest planet"\nlist names = keys planets\nprint "Solar System:"\nrepeat length names times as i\n    print names at i ":" planets at names at i',
    ),
    (
        "sc002",
        "Science: Animal sounds",
        'list animals = "cow" "dog" "cat" "duck" "sheep"\nlist sounds = "moo" "woof" "meow" "quack" "baa"\nprint "Animal Sounds:"\nrepeat length animals times as i\n    print "A" animals at i "says" sounds at i',
    ),
    (
        "sc003",
        "Science: Animal classification",
        'remember a = "dolphin"\nif a is "dolphin" or a is "whale"\n    print a "is a mammal"\nelif a is "eagle" or a is "sparrow"\n    print a "is a bird"\nelif a is "shark" or a is "salmon"\n    print a "is a fish"\nelse\n    print a "is an animal!"',
    ),
    (
        "sc004",
        "Science: Plant life cycle",
        'print "Plant Life Cycle:"\nlist stages = "Seed" "Sprout" "Seedling" "Mature" "Flower" "Fruit"\nrepeat length stages times as i\n    print i "." stages at i',
    ),
    (
        "sc005",
        "Science: Water cycle",
        'print "Water Cycle:"\nprint "1. Evaporation"\nprint "2. Condensation"\nprint "3. Precipitation"\nprint "4. Collection"\nprint "The cycle never stops!"',
    ),
    (
        "sc006",
        "Science: Food chain",
        'list chain = "Sun" "Grass" "Rabbit" "Fox"\nprint "Food Chain:"\nrepeat length chain times as i\n    if i bigger 1\n        print chain at i "eats" chain at i - 1',
    ),
    (
        "sc007",
        "Science: Body systems",
        'list sys = "Skeletal" "Muscular" "Circulatory" "Respiratory" "Digestive" "Nervous"\nprint "Body Systems:"\nrepeat length sys times as i\n    print i "." sys at i "system"',
    ),
    (
        "sc008",
        "Science: Five senses",
        'list senses = "Sight" "Hearing" "Touch" "Taste" "Smell"\nlist organs = "eyes" "ears" "skin" "tongue" "nose"\nprint "Senses:"\nrepeat 5 times as i\n    print senses at i "- we use our" organs at i',
    ),
    (
        "sc009",
        "Science: Food groups",
        'list groups = "Fruits" "Vegetables" "Grains" "Protein" "Dairy"\nprint "Food Groups:"\nrepeat length groups times as i\n    print i "." groups at i',
    ),
    (
        "sc010",
        "Science: Moon phases",
        'list phases = "New" "Waxing Crescent" "First Quarter" "Waxing Gibbous" "Full" "Waning Gibbous" "Third Quarter" "Waning Crescent"\nprint "Moon Phases:"\nrepeat length phases times as i\n    print i "." phases at i',
    ),
]
for f, title, content in progs:
    full = f"# {title}\n{content}"
    if w(d20, f + ".kd", full):
        print(f"Created: 20/{f}")

# ---- 11-file-io (remaining) ----
d11 = os.path.join(BASE, "11-file-io")
progs = [
    (
        "io009",
        "File: Shopping list to file",
        'write "Shopping:" to "shop.txt"\nappend "milk" to "shop.txt"\nappend "bread" to "shop.txt"\nappend "eggs" to "shop.txt"\nremember list_data = read "shop.txt"\nprint list_data',
    ),
    (
        "io010",
        "File: Config reader",
        'write "name=KIDO" to "config.txt"\nappend "version=1.1" to "config.txt"\nremember cfg = read "config.txt"\nprint "Config:"\nprint cfg',
    ),
    (
        "io011",
        "File: Todo from file",
        'write "TODO:" to "todo.txt"\nappend "1. Learn KIDO" to "todo.txt"\nappend "2. Write programs" to "todo.txt"\nappend "3. Have fun" to "todo.txt"\nremember t = read "todo.txt"\nprint t',
    ),
    (
        "io012",
        "File: Combine files",
        'write "Hello" to "p1.txt"\nwrite "World" to "p2.txt"\nremember a = read "p1.txt"\nremember b = read "p2.txt"\nwrite a " " b to "combined.txt"\nremember c = read "combined.txt"\nprint "Combined:" c',
    ),
    (
        "io013",
        "File: Quote keeper",
        'write "Be kind to others" to "quote.txt"\nremember q = read "quote.txt"\nprint "Quote:" q',
    ),
    (
        "io014",
        "File: Name organizer",
        'write "Alice" to "names.txt"\nappend "Bob" to "names.txt"\nappend "Charlie" to "names.txt"\nremember data = read "names.txt"\nremember names = split data "\n"\nprint "Names:"\nrepeat length names times as i\n    print i "." names at i',
    ),
    (
        "io015",
        "File: Coding journal",
        'write "Day 1: Started KIDO" to "journal.txt"\nappend "Day 2: Made a game" to "journal.txt"\nappend "Day 3: Learned files" to "journal.txt"\nremember j = read "journal.txt"\nprint "Journal:"\nprint j',
    ),
]
for f, title, content in progs:
    full = f"# {title}\n{content}"
    if w(d11, f + ".kd", full):
        print(f"Created: 11/{f}")

# ---- 13-calendar-time (more) ----
progs2 = [
    (
        "tm016",
        "Calendar: School vs holiday",
        'remember m = 7\nif m is 6 or m is 7 or m is 8\n    print "Summer vacation!"\nelse\n    print "School in session"',
    ),
    (
        "tm017",
        "Time: Minutes in a day",
        'remember mins = 24 * 60\nprint "Day has" mins "minutes"\nprint "Week has" mins * 7 "minutes"',
    ),
    (
        "tm018",
        "Calendar: Month name",
        'remember num = 7\nlist names = "Jan" "Feb" "Mar" "Apr" "May" "Jun" "Jul" "Aug" "Sep" "Oct" "Nov" "Dec"\nprint "Month" num "is" names at num',
    ),
    (
        "tm019",
        "Calendar: Sundays in month",
        'print "Most months have 4 Sundays"\nprint "Some have 5!"',
    ),
    (
        "tm020",
        "Calendar: Season activity",
        'remember s = "summer"\nif s is "summer" print "Go swimming!"\nelif s is "winter" print "Make a snowman!"\nelif s is "spring" print "Plant flowers!"\nelif s is "fall" print "Rake leaves!"',
    ),
]
for f, title, content in progs2:
    full = f"# {title}\n{content}"
    if w(d13, f + ".kd", full):
        print(f"Created: 13/{f}")

# ---- 16-probability-stats (remaining) ----
progs3 = [
    (
        "st007",
        "Stats: Heads streak",
        'remember streak = 0\nremember best = 0\nrepeat 1000 times as i\n    remember flip = random 1 2\n    if flip is 1\n        remember streak = streak + 1\n        if streak bigger best\n            remember best = streak\n    else\n        remember streak = 0\nprint "Longest heads streak:" best',
    ),
    (
        "st008",
        "Stats: Guess probability",
        'remember correct = 0\nrepeat 100 times as i\n    remember g = random 1 10\n    remember t = random 1 10\n    if g is t\n        remember correct = correct + 1\nprint "Correct guesses in 100:" correct "%"',
    ),
    (
        "st009",
        "Stats: Sum of two dice",
        'remember sums = 0 0 0 0 0 0 0 0 0 0 0\nrepeat 1000 times as i\n    remember d1 = random 1 6\n    remember d2 = random 1 6\n    remember s = d1 + d2\n    if s is 2 sums at 1 = sums at 1 + 1\n    elif s is 3 sums at 2 = sums at 2 + 1\n    elif s is 4 sums at 3 = sums at 3 + 1\n    elif s is 5 sums at 4 = sums at 4 + 1\n    elif s is 6 sums at 5 = sums at 5 + 1\n    elif s is 7 sums at 6 = sums at 6 + 1\n    elif s is 8 sums at 7 = sums at 7 + 1\n    elif s is 9 sums at 8 = sums at 8 + 1\n    elif s is 10 sums at 9 = sums at 9 + 1\n    elif s is 11 sums at 10 = sums at 10 + 1\n    elif s is 12 sums at 11 = sums at 11 + 1\nprint "Sum distribution:"\nrepeat 11 times as i\n    print i + 1 ":" sums at i',
    ),
    (
        "st010",
        "Stats: Birthday paradox",
        'remember count = 0\nrepeat 365 times as i\n    remember b = random 1 365\n    if b is 1\n        remember count = count + 1\nprint "People born Jan 1 in 365:" count\nprint "In 23 people, 50% chance two share a birthday!"',
    ),
]
for f, title, content in progs3:
    full = f"# {title}\n{content}"
    if w(d16, f + ".kd", full):
        print(f"Created: 16/{f}")

# Finish
print("\nDone! Check categories 11-20 for new files.")
