"""
Build 150 new WordTerm entries verified against local kjv.pdf (deep-research HS-1/HS-3).
Outputs: src/data/wordsExpansion.ts, src/data/expertCluesExpansion.ts, expansion-research.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
KJV_PDF = Path(r"c:\Users\fanel\Downloads\kjv.pdf")
OUT_TS = ROOT / "src" / "data" / "wordsExpansion.ts"
OUT_EXPERT = ROOT / "src" / "data" / "expertCluesExpansion.ts"
OUT_LEDGER = ROOT / "docs" / "expansion-research-ledger.json"

# Each entry: chapter meta + words with verify_substring (must appear in kjv.pdf)
EXPANSION: list[dict] = [
    {
        "id": "daniel-three",
        "title": "Daniel: The Fiery Furnace",
        "description": "Faith under Nebuchadnezzar's decree — three Hebrews and the fourth like the Son of God.",
        "seasonId": "daniel",
        "words": [
            {"id": "1", "word": "IMAGE OF GOLD", "clue": "Nebuchadnezzar's idol on the plain of Dura that all were commanded to worship.", "verse": "Daniel 3:1", "verify": "image of gold", "summary": "Earthly power demands worship; God's people must obey Him rather than human decrees."},
            {"id": "2", "word": "FALL DOWN AND WORSHIP", "clue": "The command at the sound of music when the golden image was dedicated.", "verse": "Daniel 3:5", "verify": "fall down and worship", "summary": "The test of worship is not private opinion but public allegiance when music sounds and crowds bow."},
            {"id": "3", "word": "FURNACE HEATED SEVENFOLD", "clue": "Nebuchadnezzar's rage turned the execution fire hotter than usual.", "verse": "Daniel 3:19", "verify": "seven times more than it was wont", "summary": "Opposition to truth often intensifies when faithful witnesses refuse to compromise."},
            {"id": "4", "word": "FOURTH MAN LOOSE", "clue": "The king saw one like the Son of God walking with the three in the fire.", "verse": "Daniel 3:25", "verify": "like the Son of God", "summary": "Christ walks with believers in their fiercest trials, preserving them for His glory."},
            {"id": "5", "word": "NO HURT UPON BODIES", "clue": "After the furnace, not a hair was singed nor the smell of fire passed on them.", "verse": "Daniel 3:27", "verify": "nor was an hair of their head singed", "summary": "Complete deliverance demonstrates that faith in God is safer than obedience to tyranny."},
        ],
    },
    {
        "id": "daniel-five",
        "title": "Daniel: Handwriting on the Wall",
        "description": "Belshazzar's feast, sacred vessels, and the sentence written by the divine hand.",
        "seasonId": "daniel",
        "words": [
            {"id": "1", "word": "GOLDEN VESSELS", "clue": "Temple articles profaned at Babylon's drunken feast.", "verse": "Daniel 5:2", "verify": "golden vessels", "summary": "Desecrating what is holy hastens judgment on those who mock God openly."},
            {"id": "2", "word": "FINGERS OF A MANS HAND", "clue": "The part of the hand that wrote on the palace plaster.", "verse": "Daniel 5:5", "verify": "fingers of a man's hand", "summary": "God interrupts human revelry with warnings the proud cannot ignore."},
            {"id": "3", "word": "MENE MENE TEKEL UPHARSIN", "clue": "The four words Daniel interpreted before Belshazzar.", "verse": "Daniel 5:25", "verify": "MENE, MENE, TEKEL, UPHARSIN", "summary": "Heaven weighs character and measures kingdoms; every soul is numbered before God."},
            {"id": "4", "word": "TEKEL THOU ART WEIGHED", "clue": "Daniel told the king he was found wanting in the balances.", "verse": "Daniel 5:27", "verify": "TEKEL; Thou art weighed in the balances", "summary": "No earthly throne exempts a life from God's moral evaluation."},
            {"id": "5", "word": "THAT NIGHT BELSHAZZAR", "clue": "The king of the Chaldeans was slain when the sentence fell.", "verse": "Daniel 5:30", "verify": "In that night was Belshazzar the king", "summary": "Probation closes suddenly for those who persist in defiance after clear warning."},
        ],
    },
    {
        "id": "daniel-six",
        "title": "Daniel: In the Lions' Den",
        "description": "Prayer, envy, and deliverance when the law could not be changed.",
        "seasonId": "daniel",
        "words": [
            {"id": "1", "word": "LAW OF MEDES AND PERSIANS", "clue": "A decree that could not be altered once signed by the king.", "verse": "Daniel 6:8", "verify": "law of the Medes and Persians", "summary": "Human laws may be rigid, but God's servants answer first to a higher court."},
            {"id": "2", "word": "THRICE DAILY UPON KNEES", "clue": "Daniel's open window prayer toward Jerusalem.", "verse": "Daniel 6:10", "verify": "he kneeled upon his knees three times a day", "summary": "Faithful prayer habits prepare the soul to stand when persecution comes."},
            {"id": "3", "word": "DEN OF LIONS", "clue": "The pit where Daniel was cast for praying to his God.", "verse": "Daniel 6:16", "verify": "cast him into the den of lions", "summary": "The same place meant for destruction became a testimony of divine protection."},
            {"id": "4", "word": "GOD HATH SENT HIS ANGEL", "clue": "Daniel's explanation for why the lions did not hurt him.", "verse": "Daniel 6:22", "verify": "God hath sent his angel", "summary": "Angels minister to those who serve God with an upright heart before Him."},
            {"id": "5", "word": "LIVING GOD FOREVER", "clue": "Darius decreed that Daniel's God is the living God whose kingdom shall not be destroyed.", "verse": "Daniel 6:26", "verify": "He is the living God, and stedfast for ever", "summary": "Even pagan rulers can confess that earthly thrones fade before the eternal kingdom."},
        ],
    },
    {
        "id": "daniel-nine",
        "title": "Daniel: Seventy Weeks",
        "description": "Gabriel's prophecy of Messiah the Prince and the determined vision.",
        "seasonId": "daniel",
        "words": [
            {"id": "1", "word": "SEVENTY WEEKS DETERMINED", "clue": "Time decreed upon Daniel's people and holy city in Gabriel's message.", "verse": "Daniel 9:24", "verify": "Seventy weeks are determined", "summary": "God marks out prophetic time for finishing transgression and bringing in everlasting righteousness."},
            {"id": "2", "word": "MESSIAH THE PRINCE", "clue": "The Anointed One who appears after sixty-nine weeks in the prophecy.", "verse": "Daniel 9:25", "verify": "Messiah the Prince", "summary": "Christ's first advent was foretold centuries before He entered Jerusalem."},
            {"id": "3", "word": "CUT OFF NOT FOR HIMSELF", "clue": "Messiah is cut off in the middle of the seventieth week.", "verse": "Daniel 9:26", "verify": "shall Messiah be cut off, but not for himself", "summary": "The cross was not accident but the fulfillment of heaven's appointed timetable."},
            {"id": "4", "word": "CONFIRM COVENANT ONE WEEK", "clue": "Messiah confirms the covenant during the final prophetic week.", "verse": "Daniel 9:27", "verify": "confirm the covenant with many for one week", "summary": "Christ's ministry and sacrifice ratified the new covenant with humanity."},
            {"id": "5", "word": "ABOMINATION OF DESOLATION", "clue": "Daniel links desolating abominations to the close of the seventy-weeks prophecy.", "verse": "Daniel 9:27", "verify": "abomination that maketh desolate", "summary": "False worship desolates what God consecrates — a warning repeated in later prophecy."},
        ],
    },
    {
        "id": "daniel-ten",
        "title": "Daniel: The Glorious Man",
        "description": "Vision by the Hiddekel — conflict in the unseen realm and strengthening for the prophet.",
        "seasonId": "daniel",
        "words": [
            {"id": "1", "word": "MAN CLOTHED IN LINEN", "clue": "A glorious figure girded with gold of Uphaz above the river.", "verse": "Daniel 10:5", "verify": "clothed in linen", "summary": "Heaven sends visible assurance that spiritual battles are fought under divine leadership."},
            {"id": "2", "word": "BODY LIKE BERYL", "clue": "Part of the description of the man by the river Hiddekel.", "verse": "Daniel 10:6", "verify": "His body also was like the beryl", "summary": "Prophetic visions reveal the majesty of beings who serve the throne of God."},
            {"id": "3", "word": "PRINCE OF PERSIA", "clue": "A spiritual power that withstood the angel twenty-one days.", "verse": "Daniel 10:13", "verify": "prince of the kingdom of Persia", "summary": "Behind earthly empires stand contending powers in the unseen war over nations."},
            {"id": "4", "word": "MICHAEL YOUR PRINCE", "clue": "The chief prince who came to help against the kings of Persia.", "verse": "Daniel 10:21", "verify": "Michael your prince", "summary": "Michael stands for God's people in heavenly conflict long before Daniel 12."},
            {"id": "5", "word": "STRENGTHENED FOR THE VISION", "clue": "The man touched Daniel and told him to stand upright for the message.", "verse": "Daniel 10:19", "verify": "O man greatly beloved, fear not", "summary": "God sustains His servants when revelations of end-time conflict overwhelm human strength."},
        ],
    },
    {
        "id": "exodus-sanctuary",
        "title": "Exodus: Earthly Sanctuary",
        "description": "The tabernacle pattern shown on the mount — shadow of heavenly things.",
        "words": [
            {"id": "1", "word": "PATTERN SHEWED THEE", "clue": "Moses was commanded to build the tabernacle according to the heavenly model.", "verse": "Exodus 25:9", "verify": "According to all that I shew thee, after the pattern", "summary": "The earthly sanctuary was a copy of the true tabernacle where Christ ministers."},
            {"id": "2", "word": "ARK OF THE TESTIMONY", "clue": "The chest overlaid with gold holding the tables of the law.", "verse": "Exodus 25:16", "verify": "ark of the testimony", "summary": "God's law at the heart of the sanctuary reveals the standard of His government."},
            {"id": "3", "word": "MERCY SEAT OF GOLD", "clue": "The lid where God promised to meet with Moses between the cherubim.", "verse": "Exodus 25:17", "verify": "mercy seat of pure gold", "summary": "Mercy and law meet at the throne where intercession covers repentant sinners."},
            {"id": "4", "word": "CANDLESTICK OF PURE GOLD", "clue": "Seven lamps giving light in the holy place.", "verse": "Exodus 25:31", "verify": "candlestick of pure gold", "summary": "The Spirit illuminates the church as the lampstand lit the first apartment."},
            {"id": "5", "word": "VEIL OF BLUE PURPLE", "clue": "The curtain separating the holy from the most holy place.", "verse": "Exodus 26:31", "verify": "vail of blue, and purple, and scarlet", "summary": "Access to God's presence was limited until Christ's flesh was torn for us."},
        ],
    },
    {
        "id": "leviticus-atonement",
        "title": "Leviticus: Day of Atonement",
        "description": "Annual cleansing of the sanctuary and the scapegoat bearing sin away.",
        "words": [
            {"id": "1", "word": "DAY OF ATONEMENTS", "clue": "The tenth day of the seventh month when the high priest made reconciliation.", "verse": "Leviticus 16:29", "verify": "day of atonement", "summary": "Typical services pointed forward to Christ's final work removing sin from the record."},
            {"id": "2", "word": "TWO GOATS FOR SIN", "clue": "Lots cast — one for the LORD and one for Azazel.", "verse": "Leviticus 16:8", "verify": "one lot for the LORD, and the other lot for the scapegoat", "summary": "Sin is both atoned and removed — justice satisfied and guilt borne away."},
            {"id": "3", "word": "WITHIN THE VAIL", "clue": "The high priest entered the most holy only on this day with blood.", "verse": "Leviticus 16:15", "verify": "within the vail", "summary": "Only blood could open the inner sanctuary — fulfilled in Christ's heavenly ministry."},
            {"id": "4", "word": "SCAPEGOAT BEAR SINS", "clue": "The live goat sent into the wilderness bearing the confessed transgressions.", "verse": "Leviticus 16:22", "verify": "bear upon him all their iniquities unto a land not inhabited", "summary": "Satan ultimately bears the final responsibility for sin's origin and deception."},
            {"id": "5", "word": "AFFLICT YOUR SOULS", "clue": "Israel was to humble themselves on the day of atonement.", "verse": "Leviticus 16:31", "verify": "afflict your souls", "summary": "Reconciliation with God requires heartfelt repentance, not mere ritual."},
        ],
    },
    {
        "id": "hebrews-sanctuary",
        "title": "Hebrews: Heavenly Ministry",
        "description": "Christ our High Priest in the true tabernacle pitched by the Lord.",
        "words": [
            {"id": "1", "word": "HIGH PRIEST FOREVER", "clue": "Melchisedec order — a priesthood that does not pass to another.", "verse": "Hebrews 6:20", "verify": "high priest for ever after the order of Melchisedec", "summary": "Jesus continues interceding because His priesthood never ends."},
            {"id": "2", "word": "MINISTER OF SANCTUARY", "clue": "Christ serves in the true tabernacle which the Lord pitched.", "verse": "Hebrews 8:2", "verify": "minister of the sanctuary, and of the true tabernacle", "summary": "Heaven's sanctuary is real — not metaphor but the center of salvation's administration."},
            {"id": "3", "word": "BETTER COVENANT ESTABLISHED", "clue": "The new covenant with better promises than the old.", "verse": "Hebrews 8:6", "verify": "mediator of a better covenant", "summary": "God writes His law on the heart under the covenant sealed by Christ's blood."},
            {"id": "4", "word": "ONCE IN THE END", "clue": "Christ appeared to put away sin by the sacrifice of Himself.", "verse": "Hebrews 9:26", "verify": "once in the end of the world hath he appeared", "summary": "One perfect offering ended the need for repeated animal sacrifices."},
            {"id": "5", "word": "WITHOUT SIN UNTO SALVATION", "clue": "Christ will appear the second time to those who look for Him.", "verse": "Hebrews 9:28", "verify": "without sin unto salvation", "summary": "The same Saviour who died once will return for those waiting in faith."},
        ],
    },
    {
        "id": "isaiah-comfort",
        "title": "Isaiah: Comfort My People",
        "description": "Voices in the wilderness and the glory of the LORD revealed.",
        "words": [
            {"id": "1", "word": "COMFORT YE MY PEOPLE", "clue": "Heaven's command to speak tenderly to Jerusalem.", "verse": "Isaiah 40:1", "verify": "Comfort ye, comfort ye my people", "summary": "God's message to the end-time church blends comfort with preparation."},
            {"id": "2", "word": "VOICE CRYING WILDERNESS", "clue": "Prepare the way of the LORD — make straight a highway.", "verse": "Isaiah 40:3", "verify": "voice of one crying in the wilderness", "summary": "John the Baptist and end-time heralds call hearts to level every obstacle to Christ."},
            {"id": "3", "word": "ALL FLESH IS GRASS", "clue": "Human glory fades but the word of our God stands forever.", "verse": "Isaiah 40:6", "verify": "All flesh is grass", "summary": "Prophetic study anchors the soul in what is eternal, not what withers."},
            {"id": "4", "word": "WORD OF GOD STAND FOREVER", "clue": "Contrast to fading grass and flower of the field.", "verse": "Isaiah 40:8", "verify": "word of our God shall stand for ever", "summary": "Scripture remains the unchanging foundation when cultures and empires pass."},
            {"id": "5", "word": "GIVE STRENGTH TO THE WEARY", "clue": "They that wait upon the LORD renew their strength.", "verse": "Isaiah 40:29", "verify": "He giveth power to the faint", "summary": "End-time endurance comes from waiting on God, not human enthusiasm."},
        ],
    },
    {
        "id": "isaiah-servant",
        "title": "Isaiah: The Suffering Servant",
        "description": "Messiah wounded for our transgressions and bruised for our iniquities.",
        "words": [
            {"id": "1", "word": "DESPISED AND REJECTED", "clue": "The servant had no form nor comeliness that we should desire him.", "verse": "Isaiah 53:3", "verify": "He is despised and rejected of men", "summary": "The world's rejection of Christ reveals how sin blinds hearts to beauty."},
            {"id": "2", "word": "WOUNDED FOR TRANSGRESSIONS", "clue": "He was bruised for our iniquities; chastisement brought us peace.", "verse": "Isaiah 53:5", "verify": "wounded for our transgressions", "summary": "Substitutionary suffering is the heart of the gospel and prophetic hope."},
            {"id": "3", "word": "LAID ON HIM INIQUITY", "clue": "The LORD laid on Him the iniquity of us all.", "verse": "Isaiah 53:6", "verify": "laid on him the iniquity of us all", "summary": "Christ bore collective guilt so repentant sinners might go free."},
            {"id": "4", "word": "OPENED NOT HIS MOUTH", "clue": "As a lamb to slaughter, the servant was silent before shearers.", "verse": "Isaiah 53:7", "verify": "opened not his mouth", "summary": "Messiah's silence at trial fulfilled prophecy and revealed perfect submission."},
            {"id": "5", "word": "MAKE INTERCESSION FOR TRANSGRESSORS", "clue": "He bore sin of many and makes intercession for transgressors.", "verse": "Isaiah 53:12", "verify": "made intercession for the transgressors", "summary": "The same priest who died still pleads for those who come to God through Him."},
        ],
    },
    {
        "id": "joel-prophecy",
        "title": "Joel: The Day of the LORD",
        "description": "Locust army, trumpet alarm, and Spirit outpouring before the great day.",
        "words": [
            {"id": "1", "word": "BLOW THE TRUMPET ZION", "clue": "Alarm sounded in God's holy mountain before the day of the LORD.", "verse": "Joel 2:1", "verify": "Blow ye the trumpet in Zion", "summary": "Heaven calls the church to warn the world while mercy still lingers."},
            {"id": "2", "word": "DAY OF DARKNESS GLOOMINESS", "clue": "Joel describes the day of the LORD as terrible and not to be desired.", "verse": "Joel 2:2", "verify": "day of darkness and of gloominess", "summary": "Prophetic language prepares believers for crisis without fostering fear without faith."},
            {"id": "3", "word": "POUR OUT MY SPIRIT", "clue": "God will pour Spirit on all flesh — sons and daughters prophesy.", "verse": "Joel 2:28", "verify": "I will pour out my spirit upon all flesh", "summary": "Pentecost and the latter rain share one promise — universal Spirit empowerment."},
            {"id": "4", "word": "SUN TURNED DARKNESS", "clue": "Wonders in heaven and earth before the great and terrible day.", "verse": "Joel 2:31", "verify": "The sun shall be turned into darkness", "summary": "Cosmic signs accompany both Pentecost-era fulfillment and final crisis."},
            {"id": "5", "word": "VALLEY OF DECISION", "clue": "Multitudes gathered where the day of the LORD is near.", "verse": "Joel 3:14", "verify": "valley of decision", "summary": "Every soul eventually chooses sides in the great controversy between Christ and Satan."},
        ],
    },
    {
        "id": "zechariah-temple",
        "title": "Zechariah: Branch and Builder",
        "description": "Joshua the high priest, the Branch, and the flying roll.",
        "words": [
            {"id": "1", "word": "BRAND PLUCKED FROM FIRE", "clue": "Israel pictured as a burning stick snatched from the flames.", "verse": "Zechariah 3:2", "verify": "brand plucked out of the fire", "summary": "God preserves a remnant despite their filthy garments and Satan's accusations."},
            {"id": "2", "word": "CHANGE OF RAIMENT", "clue": "Joshua stood before the angel with filthy garments removed.", "verse": "Zechariah 3:4", "verify": "change of raiment", "summary": "Justification covers the believer with Christ's righteousness in heavenly court."},
            {"id": "3", "word": "BEHOLD THE MAN BRANCH", "clue": "The name of the Branch who shall build the temple of the LORD.", "verse": "Zechariah 6:12", "verify": "Behold the man whose name is The BRANCH", "summary": "Christ builds a spiritual temple of living stones from every nation."},
            {"id": "4", "word": "NOT BY MIGHT NOR POWER", "clue": "Zerubbabel shall finish the work by My Spirit, saith the LORD.", "verse": "Zechariah 4:6", "verify": "Not by might, nor by power, but by my spirit", "summary": "Final gospel work succeeds through Spirit power, not human schemes."},
            {"id": "5", "word": "FLYING ROLL CURSE", "clue": "The curse goes forth over the whole earth against thieves and false swearers.", "verse": "Zechariah 5:3", "verify": "flying roll", "summary": "God's law still bears witness against sin in every land before judgment falls."},
        ],
    },
    {
        "id": "malachi-remnant",
        "title": "Malachi: Sun of Righteousness",
        "description": "Messenger of the covenant, robbing God, and the great and dreadful day.",
        "words": [
            {"id": "1", "word": "MESSENGER OF THE COVENANT", "clue": "The Lord whom ye seek shall suddenly come to His temple.", "verse": "Malachi 3:1", "verify": "messenger of the covenant", "summary": "John prepared the way; Christ fulfilled the covenant promise at His first advent."},
            {"id": "2", "word": "REFINERS FIRE FULLERS SOAP", "clue": "He shall sit as a refiner and purifier of the sons of Levi.", "verse": "Malachi 3:2", "verify": "refiner's fire, and like fullers' sope", "summary": "Preparation for the end purges character as fire purges metal."},
            {"id": "3", "word": "ROB GOD IN TITHES", "clue": "Israel asked wherein they had robbed God — tithes and offerings.", "verse": "Malachi 3:8", "verify": "Will a man rob God? Yet ye have robbed me", "summary": "Stewardship reveals trust in God's provision during the closing work."},
            {"id": "4", "word": "BOOK OF REMEMBRANCE", "clue": "A book written for those who feared the LORD and thought upon His name.", "verse": "Malachi 3:16", "verify": "book of remembrance was written before him", "summary": "Heaven records faithfulness that earth may forget or ridicule."},
            {"id": "5", "word": "SUN OF RIGHTEOUSNESS ARISE", "clue": "With healing in His wings to those who fear God's name.", "verse": "Malachi 4:2", "verify": "Sun of righteousness arise with healing in his wings", "summary": "The same day that burns the wicked brings healing to those who serve God."},
        ],
    },
    {
        "id": "matthew-parables",
        "title": "Matthew: Kingdom Parables",
        "description": "Ten virgins, talents, and sheep separated from goats.",
        "words": [
            {"id": "1", "word": "TEN VIRGINS WENT FORTH", "clue": "They went to meet the bridegroom — five wise and five foolish.", "verse": "Matthew 25:1", "verify": "ten virgins, which took their lamps", "summary": "Outward profession without inner oil fails when the cry sounds at midnight."},
            {"id": "2", "word": "MIDNIGHT CRY BEHOLD BRIDEGROOM", "clue": "The shout that roused the sleeping virgins to trim their lamps.", "verse": "Matthew 25:6", "verify": "at midnight there was a cry made, Behold, the bridegroom cometh", "summary": "Sudden awakening precedes Christ's return — preparation cannot be borrowed at the last moment."},
            {"id": "3", "word": "I WAS AN HUNGERED", "clue": "The King judges nations by treatment of the least of His brethren.", "verse": "Matthew 25:35", "verify": "I was an hungred, and ye gave me meat", "summary": "Practical compassion toward God's people marks those ready for the kingdom."},
            {"id": "4", "word": "DEPART FROM ME YE CURSED", "clue": "Those on the left hear sentence into everlasting fire prepared for devil and angels.", "verse": "Matthew 25:41", "verify": "Depart from me, ye cursed", "summary": "Final separation is real — character fixed in relation to Christ and His people."},
            {"id": "5", "word": "ENTER THOU GOOD SERVANT", "clue": "The faithful servant invited into the joy of the lord.", "verse": "Matthew 25:21", "verify": "Enter thou into the joy of thy lord", "summary": "Stewardship of gifts now determines participation in eternal joy."},
        ],
    },
    {
        "id": "luke-watchfulness",
        "title": "Luke: Watch and Pray",
        "description": "Fig tree lesson and readiness for the Son of man.",
        "words": [
            {"id": "1", "word": "FIG TREE PUTTETH FORTH", "clue": "When leaves appear, summer is near — so know the kingdom is nigh.", "verse": "Luke 21:29", "verify": "Behold the fig tree, and all the trees", "summary": "Signs in prophecy are meant to inspire watchfulness, not date-setting pride."},
            {"id": "2", "word": "THIS GENERATION NOT PASS", "clue": "Heaven and earth shall pass but Christ's words stand forever.", "verse": "Luke 21:32", "verify": "This generation shall not pass away", "summary": "Prophetic word is sure even when centuries unfold before fulfillment."},
            {"id": "3", "word": "TAKE HEED TO YOURSELVES", "clue": "Lest hearts be overcharged with surfeiting and cares of this life.", "verse": "Luke 21:34", "verify": "Take heed to yourselves, lest at any time your hearts be overcharged", "summary": "Spiritual drowsiness is the danger of the last days as much as open sin."},
            {"id": "4", "word": "WATCH THEREFORE AND PRAY", "clue": "Command to be counted worthy to escape and stand before the Son of man.", "verse": "Luke 21:36", "verify": "Watch ye therefore, and pray always", "summary": "Prayer keeps the soul alert for the unexpected hour of the Advent."},
            {"id": "5", "word": "REDEMPTION DRAWETH NIGH", "clue": "When these things begin to come to pass, look up.", "verse": "Luke 21:28", "verify": "your redemption draweth nigh", "summary": "Crisis for the world is hope for those whose citizenship is in heaven."},
        ],
    },
    {
        "id": "acts-restoration",
        "title": "Acts: Times of Restitution",
        "description": "Pentecost power and Peter's prophecy of all things restored.",
        "words": [
            {"id": "1", "word": "SOUND FROM HEAVEN", "clue": "Rushing mighty wind filled the house where disciples waited.", "verse": "Acts 2:2", "verify": "suddenly there came a sound from heaven", "summary": "The early rain began with audible heaven-sent power, not human organization."},
            {"id": "2", "word": "CLOVEN TONGUES LIKE FIRE", "clue": "Sat upon each of them when the Spirit was poured out.", "verse": "Acts 2:3", "verify": "cloven tongues like as of fire", "summary": "Fire symbolizes purification and proclamation accompanying Spirit baptism."},
            {"id": "3", "word": "TIMES OF RESTITUTION", "clue": "Peter said heaven must receive Christ until all things restored.", "verse": "Acts 3:21", "verify": "times of restitution of all things", "summary": "History moves toward restoration of Eden's order through Christ's reign."},
            {"id": "4", "word": "PROPHET LIKE UNTO ME", "clue": "Moses' prophecy of a Prophet the people must hear.", "verse": "Acts 3:22", "verify": "A prophet shall the Lord your God raise up unto you of your brethren, like unto me", "summary": "Christ fulfills Moses' prediction — rejecting Him repeats Israel's fatal error."},
            {"id": "5", "word": "REPENT AND BE CONVERTED", "clue": "Peter's call that sins may be blotted out when refreshing comes.", "verse": "Acts 3:19", "verify": "Repent ye therefore, and be converted", "summary": "Revival precedes latter rain — conversion opens the door to Spirit refreshing."},
        ],
    },
    {
        "id": "romans-gospel",
        "title": "Romans: Righteousness of God",
        "description": "Justification by faith and hope of the creation's deliverance.",
        "words": [
            {"id": "1", "word": "NOT ASHAMED OF GOSPEL", "clue": "Paul's theme — power of God unto salvation to every believer.", "verse": "Romans 1:16", "verify": "I am not ashamed of the gospel of Christ", "summary": "End-time witnesses proclaim the same gospel Paul defended in Rome."},
            {"id": "2", "word": "REVEALED FROM FAITH", "clue": "The just shall live by faith — righteousness of God revealed.", "verse": "Romans 1:17", "verify": "The just shall live by faith", "summary": "Habakkuk's motto became the Reformation and remains the remnant's foundation."},
            {"id": "3", "word": "ALL HAVE SINNED", "clue": "Universal need of grace — none righteous, no not one.", "verse": "Romans 3:23", "verify": "all have sinned, and come short of the glory of God", "summary": "Judgment truth begins with honest confession of universal sinfulness."},
            {"id": "4", "word": "WAGES OF SIN DEATH", "clue": "But gift of God is eternal life through Jesus Christ.", "verse": "Romans 6:23", "verify": "The wages of sin is death", "summary": "Two destinies — earned death or gifted life through Christ."},
            {"id": "5", "word": "CREATION GROANING TRAVAILETH", "clue": "Whole creation waits for manifestation of sons of God.", "verse": "Romans 8:22", "verify": "the whole creation groaneth and travaileth in pain together", "summary": "Nature itself testifies that this world is bound for liberation at the Advent."},
        ],
    },
    {
        "id": "first-corinthians-resurrection",
        "title": "1 Corinthians: Resurrection Hope",
        "description": "Last trump, corruptible must put on incorruption.",
        "words": [
            {"id": "1", "word": "LAST TRUMP SHALL SOUND", "clue": "Dead raised incorruptible when trumpet sounds at end.", "verse": "1 Corinthians 15:52", "verify": "the trumpet shall sound", "summary": "Paul links resurrection hope to the same trumpet imagery used in Revelation."},
            {"id": "2", "word": "VICTORY THROUGH LORD", "clue": "Thanks be to God who giveth us victory through Jesus Christ.", "verse": "1 Corinthians 15:57", "verify": "thanks be to God, which giveth us the victory", "summary": "Resurrection is not wishful thinking but guaranteed triumph through Christ."},
            {"id": "3", "word": "STUMBLING BLOCK TO JEWS", "clue": "Preaching Christ crucified — foolishness to Greeks, power to believers.", "verse": "1 Corinthians 1:23", "verify": "Christ crucified, unto the Jews a stumblingblock", "summary": "The cross remains the dividing line between human wisdom and saving power."},
            {"id": "4", "word": "SHEW YOU MYSTERY", "clue": "We shall not all sleep but be changed in a moment.", "verse": "1 Corinthians 15:51", "verify": "I shew you a mystery", "summary": "Living saints experience translation — a distinct end-time promise."},
            {"id": "5", "word": "CORRUPTIBLE PUT ON INCORRUPTION", "clue": "Mortal must put on immortality when victory swallows death.", "verse": "1 Corinthians 15:53", "verify": "corruptible must put on incorruption", "summary": "Glorified bodies complete salvation at the last day."},
        ],
    },
    {
        "id": "ephesians-armour",
        "title": "Ephesians: Whole Armour",
        "description": "Stand against wiles of the devil in the evil day.",
        "words": [
            {"id": "1", "word": "WRESTLE NOT AGAINST FLESH", "clue": "Our struggle is against principalities and spiritual wickedness in high places.", "verse": "Ephesians 6:12", "verify": "we wrestle not against flesh and blood", "summary": "Prophetic conflict is ultimately spiritual, though it plays out in history."},
            {"id": "2", "word": "GIRDLE OF TRUTH", "clue": "First piece of armour — stand therefore having truth about the loins.", "verse": "Ephesians 6:14", "verify": "having your loins girt about with truth", "summary": "Doctrinal integrity holds every other piece of Christian armor in place."},
            {"id": "3", "word": "SHIELD OF FAITH", "clue": "Quenches all the fiery darts of the wicked one.", "verse": "Ephesians 6:16", "verify": "shield of faith", "summary": "Trust in God's word extinguishes Satan's accusations and temptations."},
            {"id": "4", "word": "HELMET OF SALVATION", "clue": "Protects the mind in the battle for the soul.", "verse": "Ephesians 6:17", "verify": "take the helmet of salvation, and the sword of the Spirit", "summary": "Assurance of salvation guards against despair in the time of trouble."},
            {"id": "5", "word": "SWORD OF THE SPIRIT", "clue": "The word of God — only offensive weapon listed.", "verse": "Ephesians 6:17", "verify": "sword of the Spirit, which is the word of God", "summary": "Scripture is both shield and weapon in the great controversy."},
        ],
    },
    {
        "id": "thessalonians-coming",
        "title": "Thessalonians: Coming of the Lord",
        "description": "Comfort concerning those who sleep and the man of sin.",
        "words": [
            {"id": "1", "word": "COMFORT ONE ANOTHER", "clue": "Words about those asleep — sorrow not as others without hope.", "verse": "1 Thessalonians 4:18", "verify": "comfort one another with these words", "summary": "Advent hope transforms grief into anticipation for reunited saints."},
            {"id": "2", "word": "THIEF IN THE NIGHT", "clue": "Day of the Lord comes when peace and safety are declared.", "verse": "1 Thessalonians 5:2", "verify": "the day of the Lord so cometh as a thief in the night", "summary": "Suddenness catches the unprepared; watchfulness marks the faithful."},
            {"id": "3", "word": "MAN OF SIN REVEALED", "clue": "Son of perdition exalts himself above all that is called God.", "verse": "2 Thessalonians 2:3", "verify": "that man of sin be revealed", "summary": "Paul foresaw a developing apostasy before Christ's return."},
            {"id": "4", "word": "WHAT WITHHOLDETH NOW", "clue": "Something restrains until the wicked one is taken out of the way.", "verse": "2 Thessalonians 2:7", "verify": "he who now letteth will let", "summary": "Prophetic timing involves restraining forces removed before final deception."},
            {"id": "5", "word": "STAND FAST HOLD TRADITIONS", "clue": "Paul urges steadfastness in taught word whether by epistle or speech.", "verse": "2 Thessalonians 2:15", "verify": "stand fast, and hold the traditions", "summary": "End-time stability comes from holding apostolic teaching, not novel theories."},
        ],
    },
    {
        "id": "second-peter-day",
        "title": "2 Peter: Day of the Lord",
        "description": "Scoffers, new heavens and earth, and growing in grace.",
        "words": [
            {"id": "1", "word": "SCOFFERS WALKING AFTER LUST", "clue": "Mockers ask where is promise of His coming since fathers fell asleep.", "verse": "2 Peter 3:3", "verify": "there shall come in the last days scoffers", "summary": "Skepticism about the Advent is itself a sign of the last days."},
            {"id": "2", "word": "ONE DAY IS AS THOUSAND", "clue": "Lord not slack — a day with Him is as a thousand years.", "verse": "2 Peter 3:8", "verify": "one day is with the Lord as a thousand years", "summary": "Apparent delay is patience, not broken promise."},
            {"id": "3", "word": "ELEMENTS MELT FERVENT HEAT", "clue": "Heavens pass away with great noise at day of God.", "verse": "2 Peter 3:10", "verify": "elements shall melt with fervent heat", "summary": "Earth's purification by fire precedes the new creation."},
            {"id": "4", "word": "NEW HEAVENS NEW EARTH", "clue": "Peter promises dwelling wherein dwelleth righteousness after fire.", "verse": "2 Peter 3:13", "verify": "new heavens and a new earth, wherein dwelleth righteousness", "summary": "Peter's hope matches Revelation's — righteousness fills remade creation."},
            {"id": "5", "word": "GROW IN GRACE KNOWLEDGE", "clue": "Final exhortation while waiting for day of God.", "verse": "2 Peter 3:18", "verify": "grow in grace, and in the knowledge of our Lord", "summary": "Waiting time is growth time — not idle speculation."},
        ],
    },
    {
        "id": "rev-throne",
        "title": "Revelation: Throne in Heaven",
        "description": "Four beasts, twenty-four elders, and the sealed book.",
        "seasonId": "revelation",
        "words": [
            {"id": "1", "word": "THRONE SET IN HEAVEN", "clue": "John saw one sitting on the throne with emerald rainbow round about.", "verse": "Revelation 4:2", "verify": "a throne was set in heaven", "summary": "History's conflicts unfold before a occupied throne — God still reigns."},
            {"id": "2", "word": "FOUR AND TWENTY ELDERS", "clue": "They cast crowns before the throne and worship Him that lives forever.", "verse": "Revelation 4:10", "verify": "four and twenty elders", "summary": "Redeemed representatives join heaven's council worshipping the Creator."},
            {"id": "3", "word": "FOUR BEASTS FULL OF EYES", "clue": "Each unlike the other — lion, calf, man, flying eagle.", "verse": "Revelation 4:6", "verify": "four beasts full of eyes before and behind", "summary": "Heaven's intelligence covers earth with vigilant praise day and night."},
            {"id": "4", "word": "HOLY HOLY HOLY LORD", "clue": "Beasts rest not saying Holy, holy, holy, Lord God Almighty.", "verse": "Revelation 4:8", "verify": "Holy, holy, holy, Lord God Almighty", "summary": "Isaiah's sanctuary cry fills heaven — holiness is the atmosphere of God's court."},
            {"id": "5", "word": "THOU ART WORTHY CREATOR", "clue": "Worthy art thou to receive glory for thou hast created all things.", "verse": "Revelation 4:11", "verify": "thou art worthy, O Lord, to receive glory", "summary": "Creation worship anchors end-time message against evolution and secularism."},
        ],
    },
    {
        "id": "rev-144000",
        "title": "Revelation: The 144,000",
        "description": "Sealed servants from every tribe before harm to earth.",
        "seasonId": "revelation",
        "words": [
            {"id": "1", "word": "SEALED IN FOREHEADS", "clue": "Angels hold back winds until servants sealed in foreheads.", "verse": "Revelation 7:3", "verify": "sealed the servants of our God in their foreheads", "summary": "Sealing is intellectual and spiritual loyalty fixed before final plagues."},
            {"id": "2", "word": "HURT NOT EARTH SEA", "clue": "Four angels restrained until sealing complete.", "verse": "Revelation 7:3", "verify": "Hurt not the earth, neither the sea", "summary": "Mercy's bounds remain until God's people are prepared."},
            {"id": "3", "word": "NUMBERED ONE HUNDRED FORTY FOUR", "clue": "Multitude sealed — symbolic completeness from Israel's tribes.", "verse": "Revelation 7:4", "verify": "an hundred and forty and four thousand of all the tribes", "summary": "The remnant represents perfect spiritual Israel, not ethnic limitation."},
            {"id": "4", "word": "GREAT MULTITUDE NO MAN NUMBER", "clue": "White-robed multitude from all nations before the throne.", "verse": "Revelation 7:9", "verify": "a great multitude, which no man could number", "summary": "Beyond the symbolic 144,000 stands an innumerable harvest of saved."},
            {"id": "5", "word": "WASHED ROBES IN BLOOD", "clue": "They came out of great tribulation and washed robes white.", "verse": "Revelation 7:14", "verify": "washed their robes, and made them white in the blood of the Lamb", "summary": "Tribulation saints reach glory through Lamb's blood, not human merit."},
        ],
    },
    {
        "id": "rev-witnesses",
        "title": "Revelation: Two Witnesses",
        "description": "Olive trees and candlesticks prophesying in sackcloth.",
        "seasonId": "revelation",
        "words": [
            {"id": "1", "word": "TWO WITNESSES PROPHESY", "clue": "They prophesy twelve hundred sixty days clothed in sackcloth.", "verse": "Revelation 11:3", "verify": "my two witnesses", "summary": "Scripture and Spirit testify through prophetic periods of oppression."},
            {"id": "2", "word": "TWO OLIVE TREES", "clue": "Standing before the God of the whole earth.", "verse": "Revelation 11:4", "verify": "two olive trees, and the two candlesticks", "summary": "Zechariah's imagery links oil of Spirit with lamp of word."},
            {"id": "3", "word": "FIRE PROCEED OUT MOUTH", "clue": "Witnesses devour enemies with fire from their mouths.", "verse": "Revelation 11:5", "verify": "fire proceedeth out of their mouth", "summary": "God's word through witnesses consumes opposition as Jeremiah foretold."},
            {"id": "4", "word": "DEAD BODIES THREE DAYS", "clue": "Beast kills witnesses; bodies lie in street of great city.", "verse": "Revelation 11:8", "verify": "dead bodies shall lie in the street", "summary": "Temporary suppression of testimony precedes dramatic vindication."},
            {"id": "5", "word": "SPIRIT OF LIFE FROM GOD", "clue": "Breath enters witnesses; great fear falls on beholders.", "verse": "Revelation 11:11", "verify": "Spirit of life from God entered into them", "summary": "Revived testimony after apparent defeat marks latter rain power."},
        ],
    },
    {
        "id": "rev-woman-dragon",
        "title": "Revelation: Woman and Dragon",
        "description": "War in heaven, wilderness nurture, and flood from the serpent.",
        "seasonId": "revelation",
        "words": [
            {"id": "1", "word": "GREAT RED DRAGON", "clue": "Seven heads and ten horns — old serpent called Devil and Satan.", "verse": "Revelation 12:3", "verify": "a great red dragon", "summary": "Behind earthly persecution stands the dragon who hates the woman's seed."},
            {"id": "2", "word": "MICHAEL FOUGHT DRAGON", "clue": "War in heaven; dragon cast out with his angels.", "verse": "Revelation 12:7", "verify": "Michael and his angels fought against the dragon", "summary": "Cosmic conflict intensifies as probation nears its close."},
            {"id": "3", "word": "ACCUSER OF BRETHREN", "clue": "Devil cast down who accused them before God day and night.", "verse": "Revelation 12:10", "verify": "accused them before our God day and night", "summary": "Nearness of Advent means Satan's accusations increase but are overcome by the Lamb."},
            {"id": "4", "word": "WILDERNESS PREPARED WOMAN", "clue": "Woman fled where she is nourished twelve hundred sixty days.", "verse": "Revelation 12:6", "verify": "wilderness, where she hath a place prepared of God", "summary": "God sustains the church through prophetic periods of hiding and persecution."},
            {"id": "5", "word": "EARTH OPENED MOUTH", "clue": "Earth helped woman and swallowed flood from dragon's mouth.", "verse": "Revelation 12:16", "verify": "the earth opened her mouth, and swallowed up the flood", "summary": "Providence shields the remnant when human and demonic forces combine."},
        ],
    },
    {
        "id": "rev-harvest",
        "title": "Revelation: Harvest of Earth",
        "description": "Three angels' messages, sickle, and winepress of wrath.",
        "seasonId": "revelation",
        "words": [
            {"id": "1", "word": "EVERLASTING GOSPEL PREACH", "clue": "Angel with gospel to every nation, kindred, tongue, and people.", "verse": "Revelation 14:6", "verify": "everlasting gospel to preach unto them that dwell on the earth", "summary": "First angel's message is gospel-centered, not merely judgment."},
            {"id": "2", "word": "FALL DOWN WORSHIP HIM", "clue": "Fear God and give glory — for hour of judgment is come.", "verse": "Revelation 14:7", "verify": "Fear God, and give glory to him", "summary": "Creator worship is the answer to evolutionary and spiritualistic deception."},
            {"id": "3", "word": "PATIENCE OF SAINTS", "clue": "Here are they that keep commandments and faith of Jesus.", "verse": "Revelation 14:12", "verify": "Here is the patience of the saints", "summary": "Remnant identity combines law and gospel — commandments and Jesus' faith."},
            {"id": "4", "word": "ONE LIKE SON OF MAN", "clue": "Sitting on white cloud with golden crown and sharp sickle.", "verse": "Revelation 14:14", "verify": "upon the cloud one sat like unto the Son of man", "summary": "Harvest imagery points to closing work separating wheat from tares."},
            {"id": "5", "word": "WINEPRESS TRODDEN WITHOUT", "clue": "Blood to horses' bridles for thousand six hundred furlongs.", "verse": "Revelation 14:20", "verify": "winepress was trodden without the city", "summary": "Judgment on oppressors follows gospel rejection."},
        ],
    },
    {
        "id": "rev-plagues",
        "title": "Revelation: Seven Last Plagues",
        "description": "Vials of wrath upon those with mark of the beast.",
        "seasonId": "revelation",
        "words": [
            {"id": "1", "word": "SEVEN GOLDEN VIALS", "clue": "Seven angels with seven plagues — last plagues filled with wrath of God.", "verse": "Revelation 15:7", "verify": "seven golden vials full of the wrath of God", "summary": "Final judgments fall without mixture of mercy on hardened rebels."},
            {"id": "2", "word": "NOISOME GRIEVOUS SORE", "clue": "First vial upon men which had mark of beast and worshipped image.", "verse": "Revelation 16:2", "verify": "noisome and grievous sore", "summary": "Plagues target allegiance to the beast system, not random suffering."},
            {"id": "3", "word": "POURED OUT HIS VIAL UPON SEA", "clue": "Second angel turns sea to blood as of a dead man.", "verse": "Revelation 16:3", "verify": "poured out his vial upon the sea", "summary": "Creation itself bears witness against rebellion in the plague era."},
            {"id": "4", "word": "EUPHRATES DRIED UP", "clue": "Sixth vial prepares way for kings of the east.", "verse": "Revelation 16:12", "verify": "Euphrates; and the water thereof was dried up", "summary": "Prophetic geography symbolizes removal of barriers before final gathering."},
            {"id": "5", "word": "IT IS DONE", "clue": "Great voice from throne declares completion when seventh vial poured.", "verse": "Revelation 16:17", "verify": "And the seventh angel poured out his vial into the air", "summary": "Heaven announces the end of mercy's mixed cup — probation closed."},
        ],
    },
    {
        "id": "rev-harlot",
        "title": "Revelation: Mystery Babylon",
        "description": "Harlot on scarlet beast and fall of great city.",
        "seasonId": "revelation",
        "words": [
            {"id": "1", "word": "MYSTERY BABYLON GREAT", "clue": "Woman on scarlet beast full of names of blasphemy.", "verse": "Revelation 17:5", "verify": "MYSTERY, BABYLON THE GREAT", "summary": "Religious apostasy rides political power in end-time coalition."},
            {"id": "2", "word": "DRUNK WITH BLOOD SAINTS", "clue": "Harlot drunken with blood of martyrs of Jesus.", "verse": "Revelation 17:6", "verify": "drunken with the blood of the saints", "summary": "Persecution history identifies systems hostile to commandment keepers."},
            {"id": "3", "word": "TEN HORNS UPON BEAST", "clue": "Horns hate harlot and make her desolate and naked.", "verse": "Revelation 17:16", "verify": "the ten horns which thou sawest upon the beast", "summary": "Earthly allies eventually turn on ecclesiastical Babylon."},
            {"id": "4", "word": "MIGHTY ANGEL CRIED", "clue": "Babylon the great is fallen, is fallen — before second angel's echo.", "verse": "Revelation 18:2", "verify": "Babylon the great is fallen, is fallen", "summary": "Moral fall precedes political collapse of confused religious systems."},
            {"id": "5", "word": "THY MERCHANDISE OF GOLD", "clue": "Kings of earth mourn when Babylon's commerce ceases in one hour.", "verse": "Revelation 18:12", "verify": "The merchandise of gold, and silver", "summary": "Economic entanglement with Babylon makes separation costly but necessary."},
        ],
    },
    {
        "id": "rev-victory",
        "title": "Revelation: Marriage and Victory",
        "description": "White horse, marriage supper, and lake of fire.",
        "seasonId": "revelation",
        "words": [
            {"id": "1", "word": "FAITHFUL AND TRUE RIDER", "clue": "Heaven opens — rider on white horse called Faithful and True.", "verse": "Revelation 19:11", "verify": "called Faithful and True", "summary": "Christ returns as warrior-king, not secret rapture thief only."},
            {"id": "2", "word": "ARMIES IN HEAVEN FOLLOW", "clue": "Armies on white horses clothed in fine linen follow the Word of God.", "verse": "Revelation 19:14", "verify": "the armies which were in heaven followed him", "summary": "Saints join the final campaign as glorified companions of Christ."},
            {"id": "3", "word": "MARRIAGE OF LAMB COME", "clue": "Wife made herself ready — fine linen is righteousness of saints.", "verse": "Revelation 19:7", "verify": "the marriage of the Lamb is come", "summary": "Corporate readiness of church precedes eternal union with Bridegroom."},
            {"id": "4", "word": "LAKE OF FIRE BURNING", "clue": "Beast and false prophet cast alive into lake of fire.", "verse": "Revelation 19:20", "verify": "cast alive into a lake of fire burning with brimstone", "summary": "Judgment on leaders of rebellion precedes broader final destruction."},
            {"id": "5", "word": "DEVIL CAST INTO LAKE", "clue": "After millennium, devil cast into lake where beast and false prophet are.", "verse": "Revelation 20:10", "verify": "devil that deceived them was cast into the lake of fire", "summary": "Sin problem ends when author of deception is destroyed forever."},
        ],
    },
    {
        "id": "rev-new-creation",
        "title": "Revelation: New Creation",
        "description": "River of life, tree of life, and invitation to come.",
        "seasonId": "revelation",
        "words": [
            {"id": "1", "word": "TABERNACLE OF GOD WITH MEN", "clue": "God shall dwell with them — they shall be His people.", "verse": "Revelation 21:3", "verify": "tabernacle of God is with men", "summary": "Eden lost becomes Eden restored with God living among redeemed."},
            {"id": "2", "word": "ALPHA AND OMEGA BEGINNING", "clue": "He that sat on throne — I am Alpha and Omega, the beginning and the end.", "verse": "Revelation 21:6", "verify": "I am Alpha and Omega, the beginning and the end", "summary": "Christ who started creation completes it in the new earth."},
            {"id": "3", "word": "RIVER OF WATER OF LIFE", "clue": "Clear as crystal proceeding from throne of God and of the Lamb.", "verse": "Revelation 22:1", "verify": "pure river of water of life", "summary": "Eternal life flows from the throne — no separation from source."},
            {"id": "4", "word": "TREE OF LIFE FRUIT", "clue": "Leaves for healing of nations on either side of the river.", "verse": "Revelation 22:2", "verify": "tree of life, which bare twelve manner of fruits", "summary": "Access forbidden at Eden's fall is restored for eternity."},
            {"id": "5", "word": "SPIRIT AND BRIDE SAY COME", "clue": "Let him that heareth say Come — whosoever will take water of life freely.", "verse": "Revelation 22:17", "verify": "the Spirit and the bride say, Come", "summary": "Even at Scripture's close, gospel invitation remains open until probation ends."},
        ],
    },
]


def load_pdf_text() -> list[str]:
    if not KJV_PDF.exists():
        sys.exit(f"Missing KJV PDF: {KJV_PDF}")
    reader = PdfReader(str(KJV_PDF))
    return [(p.extract_text() or "") for p in reader.pages]


def normalize_pdf_text(text: str) -> str:
    """Collapse PDF line breaks and unify apostrophe variants for substring search."""
    text = text.replace("\u2019", "'").replace("\u2018", "'").replace("\ufffd", "'")
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_page(pages: list[str], needle: str) -> int | None:
    n = normalize_pdf_text(needle).lower()
    for i, text in enumerate(pages):
        if n in normalize_pdf_text(text).lower():
            return i + 1
    return None


def extract_snippet(pages: list[str], page: int, verify: str, max_len: int = 240) -> str:
    """Extract a KJV snippet around verify, snapped to a clean sentence/word start."""
    text = normalize_pdf_text(pages[page - 1])
    idx = text.lower().find(normalize_pdf_text(verify).lower())
    if idx < 0:
        return verify
    start = idx
    window = text[max(0, idx - 80) : idx]
    for marker in (" And ", " For ", " But ", " Then ", " Now ", ". "):
        mpos = window.rfind(marker)
        if mpos >= 0:
            start = max(0, idx - 80) + mpos + (2 if marker == ". " else 0)
            break
    else:
        lead = max(0, idx - 20)
        while lead > 0 and text[lead - 1].isalnum():
            lead -= 1
        start = lead
    end = min(len(text), idx + max_len)
    snippet = text[start:end].replace("\n", " ")
    snippet = re.sub(r"(\d)([A-Za-z])", r"\1 \2", snippet)
    snippet = re.sub(r"\s+", " ", snippet).strip()
    snippet = re.sub(r"^\d+\s+", "", snippet)
    if snippet and snippet[0].islower():
        parts = snippet.split(" ", 1)
        snippet = parts[1] if len(parts) == 2 and len(parts[0]) <= 5 else (snippet[0].upper() + snippet[1:])
    return snippet


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")


def main() -> None:
    existing_words_path = ROOT / "src" / "data" / "words.ts"
    existing_text = existing_words_path.read_text(encoding="utf-8")
    existing_words = set(re.findall(r'word: "([^"]+)"', existing_text))

    pages = load_pdf_text()
    ledger: list[dict] = []
    chapters_out: list[dict] = []
    expert: dict[str, str] = {}

    for ch in EXPANSION:
        ch_words = []
        for w in ch["words"]:
            wid = f"{ch['id']}-{w['id']}"
            phrase = w["word"].upper()
            if phrase in existing_words:
                raise SystemExit(f"Duplicate existing word: {phrase}")
            page = find_page(pages, w["verify"])
            if page is None:
                raise SystemExit(f"KJV verify failed for {wid}: {w['verify']!r}")
            scripture = extract_snippet(pages, page, w["verify"])
            ledger.append({
                "id": wid,
                "word": phrase,
                "verse": w["verse"],
                "verify_substring": w["verify"],
                "kjv_pdf_page": page,
                "grade": "VERIFIED",
                "source": str(KJV_PDF),
                "retrieved": "2026-07-09",
            })
            ch_words.append({
                "id": wid,
                "word": phrase,
                "clue": w["clue"],
                "verse": w["verse"],
                "scripture": scripture,
                "summary": w["summary"],
            })
            expert[wid] = f"{w['verse']} — {w['verify'][:60]}"
            existing_words.add(phrase)
        chapters_out.append({
            "id": ch["id"],
            "title": ch["title"],
            "description": ch["description"],
            "seasonId": ch.get("seasonId"),
            "words": ch_words,
        })

    if len(ledger) != 150:
        raise SystemExit(f"Expected 150 words, got {len(ledger)}")

    OUT_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    OUT_LEDGER.write_text(json.dumps(ledger, indent=2), encoding="utf-8")

    ts_lines = [
        'import type { Chapter } from "./words";',
        "",
        "/** 150 KJV-verified expansion terms (2026-07-09, kjv.pdf ledger in docs/expansion-research-ledger.json). */",
        "export const expansionChapters: Chapter[] = [",
    ]
    for ch in chapters_out:
        ts_lines.append("  {")
        ts_lines.append(f"    id: '{esc(ch['id'])}',")
        ts_lines.append(f"    title: '{esc(ch['title'])}',")
        ts_lines.append(f"    description: '{esc(ch['description'])}',")
        if ch.get("seasonId"):
            ts_lines.append(f"    seasonId: '{esc(ch['seasonId'])}',")
        ts_lines.append("    words: [")
        for w in ch["words"]:
            ts_lines.append("      {")
            ts_lines.append(f"        id: '{esc(w['id'])}',")
            ts_lines.append(f"        word: '{esc(w['word'])}',")
            ts_lines.append(f"        clue: '{esc(w['clue'])}',")
            ts_lines.append(f"        verse: '{esc(w['verse'])}',")
            ts_lines.append(f"        scripture: '{esc(w['scripture'])}',")
            ts_lines.append(f"        summary: '{esc(w['summary'])}'")
            ts_lines.append("      },")
        ts_lines.append("    ]")
        ts_lines.append("  },")
    ts_lines.append("];")
    ts_lines.append("")
    OUT_TS.write_text("\n".join(ts_lines), encoding="utf-8")

    expert_lines = [
        "/** Expert clues for expansion words — merged into expertClueMap. */",
        "export const expertClueExpansion: Record<string, string> = {",
    ]
    for k, v in expert.items():
        expert_lines.append(f'  "{k}": "{esc(v)}",')
    expert_lines.append("};")
    expert_lines.append("")
    OUT_EXPERT.write_text("\n".join(expert_lines), encoding="utf-8")

    print(f"Wrote {len(ledger)} words to {OUT_TS}")
    print(f"Ledger: {OUT_LEDGER}")


if __name__ == "__main__":
    main()
