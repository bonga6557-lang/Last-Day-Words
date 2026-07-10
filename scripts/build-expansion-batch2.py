"""
Build 150 new KJV-verified WordTerms (2026-07-10):
  - 20 top-ups into original 4-word chapters (signs-5 … deceptions-5 etc.)
  - 26 new chapters × 5 words = 130

Answers are contiguous KJV phrases (prefer exact quotes; GC themes in summaries).
Outputs: wordsExpansion2.ts, expertCluesExpansion2.ts, topup patches applied to words.ts,
         docs/expansion-batch2-ledger.json
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
KJV_PDF = Path(os.environ.get("KJV_PDF", str(Path.home() / "Downloads" / "kjv.pdf")))
OUT_TS = ROOT / "src" / "data" / "wordsExpansion2.ts"
OUT_EXPERT = ROOT / "src" / "data" / "expertCluesExpansion2.ts"
OUT_LEDGER = ROOT / "docs" / "expansion-batch2-ledger.json"
WORDS_TS = ROOT / "src" / "data" / "words.ts"
EXPANSION_TS = ROOT / "src" / "data" / "wordsExpansion.ts"

# Top-ups: one word added to each original 4-word chapter
TOPUPS: list[dict] = [
    {"chapter": "signs", "id": "signs-5", "word": "NATION SHALL RISE AGAINST NATION", "clue": "Jesus lists international conflict among signs of the end in the Olivet discourse.", "verse": "Matthew 24:7", "verify": "nation shall rise against nation", "summary": "Global unrest is a solemn reminder that history moves toward the promised return of Christ."},
    {"chapter": "shaking", "id": "shaking-5", "word": "THINGS WHICH CANNOT BE SHAKEN", "clue": "What remains after God removes what can be shaken.", "verse": "Hebrews 12:27", "verify": "things which cannot be shaken may remain", "summary": "Only truth rooted in God endures the final shaking of church and world."},
    {"chapter": "latter-rain", "id": "latter-rain-5", "word": "YOUR SONS AND YOUR DAUGHTERS SHALL PROPHESY", "clue": "Joel’s promise of Spirit on all flesh before the great day.", "verse": "Joel 2:28", "verify": "your sons and your daughters shall prophesy", "summary": "The latter rain empowers the final gospel witness as Pentecost empowered the first."},
    {"chapter": "loud-cry", "id": "loud-cry-5", "word": "EARTH WAS LIGHTENED WITH HIS GLORY", "clue": "Revelation 18 angel illuminates the whole earth with glory.", "verse": "Revelation 18:1", "verify": "the earth was lightened with his glory", "summary": "The loud cry is not mere volume but global revelation of God’s character and warning."},
    {"chapter": "seal-of-god", "id": "seal-of-god-5", "word": "SEAL THE LAW AMONG MY DISCIPLES", "clue": "Isaiah links sealing God’s law among those who wait for Him.", "verse": "Isaiah 8:16", "verify": "Bind up the testimony, seal the law among my disciples", "summary": "God’s seal involves loyalty to His law written in heart and life."},
    {"chapter": "time-of-trouble", "id": "time-of-trouble-5", "word": "MICHAEL SHALL STAND UP", "clue": "Daniel’s great prince stands for his people in unprecedented trouble.", "verse": "Daniel 12:1", "verify": "Michael stand up, the great prince", "summary": "Deliverance is personal and divine when human mediation is finished."},
    {"chapter": "second-coming", "id": "second-coming-5", "word": "EVERY EYE SHALL SEE HIM", "clue": "John’s description of the public, visible return of Christ.", "verse": "Revelation 1:7", "verify": "every eye shall see him", "summary": "The Advent is not secret; the whole world will know when the King returns."},
    {"chapter": "new-earth", "id": "new-earth-5", "word": "FORMER THINGS ARE PASSED AWAY", "clue": "God’s promise after tears and death are gone from the new creation.", "verse": "Revelation 21:4", "verify": "for the former things are passed away", "summary": "Sin’s history ends; the redeemed inherit a world where pain is only a memory."},
    {"chapter": "judgment", "id": "judgment-5", "word": "BOOKS WERE OPENED", "clue": "Daniel’s court scene before the Ancient of days.", "verse": "Daniel 7:10", "verify": "the judgment was set, and the books were opened", "summary": "Heaven’s records undergird a fair judgment before the sentence of the ages."},
    {"chapter": "deceptions", "id": "deceptions-5", "word": "LYING WONDERS", "clue": "Paul warns of Satan’s power with signs and lying wonders after the working of the lawless one.", "verse": "2 Thessalonians 2:9", "verify": "all power and signs and lying wonders", "summary": "Miracles alone never prove truth; the Word is the test of every wonder."},
    {"chapter": "daniel-image", "id": "daniel-image-5", "word": "GOD OF HEAVEN SET UP A KINGDOM", "clue": "Daniel interprets the stone kingdom that fills the whole earth.", "verse": "Daniel 2:44", "verify": "the God of heaven set up a kingdom", "summary": "Human empires fall; Christ’s kingdom alone is everlasting."},
    {"chapter": "daniel-beasts", "id": "daniel-beasts-5", "word": "FOUR KINGS WHICH SHALL ARISE", "clue": "Angel’s plain interpretation of the four great beasts from the sea.", "verse": "Daniel 7:17", "verify": "These great beasts, which are four, are four kings", "summary": "Prophecy decodes empire after empire until the saints receive the kingdom."},
    {"chapter": "daniel-horn", "id": "daniel-horn-5", "word": "WEAR OUT THE SAINTS", "clue": "The little horn makes war on the holy ones for a prophetic time.", "verse": "Daniel 7:25", "verify": "shall wear out the saints of the most High", "summary": "Persecuting power is limited by heaven’s calendar; saints outlast the horn."},
    {"chapter": "daniel-sanctuary", "id": "daniel-sanctuary-5", "word": "HOW LONG SHALL BE THE VISION", "clue": "The holy one’s question that introduces the 2300 days.", "verse": "Daniel 8:13", "verify": "How long shall be the vision", "summary": "Longest prophetic timeline anchors hope in the cleansing of the sanctuary."},
    {"chapter": "daniel-stand", "id": "daniel-stand-5", "word": "KNOWLEDGE SHALL BE INCREASED", "clue": "End-time running to and fro with increase of knowledge.", "verse": "Daniel 12:4", "verify": "knowledge shall be increased", "summary": "Sealed prophecy opens as the time of the end arrives."},
    {"chapter": "rev-churches", "id": "rev-churches-5", "word": "BE ZEALOUS THEREFORE AND REPENT", "clue": "Christ’s counsel to lukewarm Laodicea.", "verse": "Revelation 3:19", "verify": "be zealous therefore, and repent", "summary": "Love rebukes; repentance restores the end-time church to usefulness."},
    {"chapter": "rev-seals", "id": "rev-seals-5", "word": "HOW LONG O LORD HOLY AND TRUE", "clue": "Cry of the fifth-seal martyrs under the altar.", "verse": "Revelation 6:10", "verify": "How long, O Lord, holy and true", "summary": "Justice delayed is not justice denied; God answers in His time."},
    {"chapter": "rev-trumpets", "id": "rev-trumpets-5", "word": "SEVEN ANGELS WHICH HAD THE SEVEN TRUMPETS", "clue": "Angels prepared to sound the judgments of the trumpets.", "verse": "Revelation 8:6", "verify": "seven angels which had the seven trumpets", "summary": "Trumpets warn the world while mercy still mingles with judgment."},
    {"chapter": "rev-beast", "id": "rev-beast-5", "word": "KEEP THE COMMANDMENTS OF GOD", "clue": "Remnant mark with the faith of Jesus in Revelation 14.", "verse": "Revelation 14:12", "verify": "keep the commandments of God, and the faith of Jesus", "summary": "Commandments of God and faith of Jesus define those who endure."},
    {"chapter": "rev-millennium", "id": "rev-millennium-5", "word": "THEY LIVED AND REIGNED WITH CHRIST", "clue": "Those in the first resurrection reign with Christ a thousand years.", "verse": "Revelation 20:4", "verify": "they lived and reigned with Christ a thousand years", "summary": "The millennium is victory for the redeemed and judgment review with Christ."},
]

# 26 new chapters × 5 = 130 words (GC-aligned themes, KJV answers)
NEW_CHAPTERS: list[dict] = [
    {
        "id": "genesis-beginnings",
        "title": "Genesis: Creation and Fall",
        "description": "Origins, Sabbath rest, and the promise after the fall — foundation of last-day hope.",
        "words": [
            {"id": "1", "word": "IN THE BEGINNING GOD CREATED", "clue": "Opening line of Scripture establishing God as Creator.", "verse": "Genesis 1:1", "verify": "In the beginning God created the heaven and the earth", "summary": "Creation anchors the Sabbath and the three angels’ call to worship the Maker."},
            {"id": "2", "word": "GOD BLESSED THE SEVENTH DAY", "clue": "The day God sanctified after finishing His work.", "verse": "Genesis 2:3", "verify": "God blessed the seventh day, and sanctified it", "summary": "Sabbath is a creation memorial, not a Jewish invention."},
            {"id": "3", "word": "DUST THOU ART", "clue": "Sentence on Adam after the fall — mortality announced.", "verse": "Genesis 3:19", "verify": "dust thou art, and unto dust shalt thou return", "summary": "Death is the wage of sin; resurrection is the gift of Christ."},
            {"id": "4", "word": "ENMITY BETWEEN THEE AND THE WOMAN", "clue": "First gospel promise spoken to the serpent.", "verse": "Genesis 3:15", "verify": "enmity between thee and the woman", "summary": "The great controversy began in Eden and ends with the serpent crushed."},
            {"id": "5", "word": "NOAH FOUND GRACE", "clue": "Why one man was spared when the earth was filled with violence.", "verse": "Genesis 6:8", "verify": "Noah found grace in the eyes of the LORD", "summary": "As in Noah’s day, grace saves a remnant before judgment falls."},
        ],
    },
    {
        "id": "exodus-sabbath",
        "title": "Exodus: Law and Sabbath",
        "description": "Covenant law, the fourth commandment, and a people sealed as God’s own.",
        "words": [
            {"id": "1", "word": "REMEMBER THE SABBATH DAY", "clue": "Opening of the fourth commandment.", "verse": "Exodus 20:8", "verify": "Remember the sabbath day, to keep it holy", "summary": "Remembrance of creation and redemption meet in the Sabbath command."},
            {"id": "2", "word": "SIX DAYS SHALT THOU LABOUR", "clue": "Work week bounded by holy rest.", "verse": "Exodus 20:9", "verify": "Six days shalt thou labour, and do all thy work", "summary": "Sabbath blessing includes faithful labor and holy rest."},
            {"id": "3", "word": "THE SEVENTH DAY IS THE SABBATH", "clue": "Plain identity of the day belonging to the LORD thy God.", "verse": "Exodus 20:10", "verify": "the seventh day is the sabbath of the LORD thy God", "summary": "God names the day; human tradition cannot rename His holy time."},
            {"id": "4", "word": "FOR IN SIX DAYS THE LORD", "clue": "Creation reason attached to the Sabbath command.", "verse": "Exodus 20:11", "verify": "For in six days the LORD made heaven and earth", "summary": "Creator worship is the issue of the final crisis."},
            {"id": "5", "word": "TABLES OF STONE", "clue": "Material on which God wrote the Ten Commandments.", "verse": "Exodus 31:18", "verify": "tables of stone, written with the finger of God", "summary": "The law is as enduring as the finger that wrote it."},
        ],
    },
    {
        "id": "isaiah-sabbath",
        "title": "Isaiah: True Sabbath Keeping",
        "description": "Isaiah 58’s call to delight in the holy day of the Lord.",
        "words": [
            {"id": "1", "word": "CALL THE SABBATH A DELIGHT", "clue": "Isaiah’s description of true Sabbath joy.", "verse": "Isaiah 58:13", "verify": "call the sabbath a delight", "summary": "Sabbath is gift, not burden, when the heart loves the Giver."},
            {"id": "2", "word": "HOLY OF THE LORD HONOURABLE", "clue": "How the Sabbath is to be called by those who honor God.", "verse": "Isaiah 58:13", "verify": "the holy of the LORD, honourable", "summary": "Reverence for God’s day reveals reverence for God’s character."},
            {"id": "3", "word": "NOT DOING THINE OWN WAYS", "clue": "Sabbath restraint of self-seeking pleasure and speech.", "verse": "Isaiah 58:13", "verify": "not doing thine own ways", "summary": "Holy time frees us from self to serve God and neighbor."},
            {"id": "4", "word": "THEN SHALT THOU DELIGHT THYSELF", "clue": "Promise to those who keep Sabbath from polluting it.", "verse": "Isaiah 58:14", "verify": "Then shalt thou delight thyself in the LORD", "summary": "Delight in God is the reward of true Sabbath rest."},
            {"id": "5", "word": "RIDE UPON THE HIGH PLACES", "clue": "Isaiah’s promise of elevated privilege for Sabbath keepers.", "verse": "Isaiah 58:14", "verify": "I will cause thee to ride upon the high places of the earth", "summary": "Faithful loyalty is honored even when the world despises it."},
        ],
    },
    {
        "id": "ezekiel-watchman",
        "title": "Ezekiel: Watchman on the Walls",
        "description": "Bloodguilt, warning, and the duty to sound the alarm.",
        "words": [
            {"id": "1", "word": "SON OF MAN I HAVE MADE THEE A WATCHMAN", "clue": "God’s commission to Ezekiel for the house of Israel.", "verse": "Ezekiel 3:17", "verify": "I have made thee a watchman unto the house of Israel", "summary": "Last-day messengers share the watchman’s duty to warn."},
            {"id": "2", "word": "HEAR THE WORD AT MY MOUTH", "clue": "Source of the watchman’s message — not human opinion.", "verse": "Ezekiel 3:17", "verify": "hear the word at my mouth, and give them warning from me", "summary": "Authority rests in God’s word spoken in love."},
            {"id": "3", "word": "HIS BLOOD WILL I REQUIRE", "clue": "Consequence if the watchman fails to warn the wicked.", "verse": "Ezekiel 3:18", "verify": "his blood will I require at thine hand", "summary": "Silence when truth is needed is not neutrality."},
            {"id": "4", "word": "THOU HAST DELIVERED THY SOUL", "clue": "Result when the watchman warns even if the hearer refuses.", "verse": "Ezekiel 3:19", "verify": "thou hast delivered thy soul", "summary": "Faithful witness frees the messenger; hearers still choose."},
            {"id": "5", "word": "I HAVE NO PLEASURE IN THE DEATH", "clue": "God’s heart toward the wicked who turn from their way.", "verse": "Ezekiel 33:11", "verify": "I have no pleasure in the death of the wicked", "summary": "Judgment is real, yet God’s desire is repentance and life."},
        ],
    },
    {
        "id": "daniel-one",
        "title": "Daniel: Faithful in Babylon",
        "description": "Purpose of heart, diet test, and wisdom from God.",
        "seasonId": "daniel",
        "words": [
            {"id": "1", "word": "DANIEL PURPOSED IN HIS HEART", "clue": "Daniel’s resolve not to defile himself with the king’s meat.", "verse": "Daniel 1:8", "verify": "Daniel purposed in his heart that he would not defile himself", "summary": "Character decisions made early sustain faithfulness later."},
            {"id": "2", "word": "PULSE TO EAT AND WATER TO DRINK", "clue": "The ten-day diet request of the four Hebrews.", "verse": "Daniel 1:12", "verify": "pulse to eat, and water to drink", "summary": "Temperance is part of last-day preparation for clear minds."},
            {"id": "3", "word": "TEN TIMES BETTER", "clue": "How the four compared to magicians after God’s blessing.", "verse": "Daniel 1:20", "verify": "ten times better than all the magicians", "summary": "God honors those who honor Him in ordinary choices."},
            {"id": "4", "word": "GOD GAVE THEM KNOWLEDGE", "clue": "Source of the youths’ skill in learning and wisdom.", "verse": "Daniel 1:17", "verify": "God gave them knowledge and skill in all learning", "summary": "True education unites intellect with loyalty to God."},
            {"id": "5", "word": "DANIEL CONTINUED EVEN UNTO", "clue": "Daniel’s long service spanning multiple empires.", "verse": "Daniel 1:21", "verify": "Daniel continued even unto the first year of king Cyrus", "summary": "Faithfulness is a lifetime race, not a single test."},
        ],
    },
    {
        "id": "habakkuk-vision",
        "title": "Habakkuk: Write the Vision",
        "description": "Watchtower faith and the just who live by faith.",
        "words": [
            {"id": "1", "word": "WRITE THE VISION", "clue": "Command to make the vision plain upon tables.", "verse": "Habakkuk 2:2", "verify": "Write the vision, and make it plain upon tables", "summary": "Prophetic truth must be clear enough to run with."},
            {"id": "2", "word": "THAT HE MAY RUN THAT READETH", "clue": "Purpose of writing the vision plainly.", "verse": "Habakkuk 2:2", "verify": "that he may run that readeth it", "summary": "Understanding moves the feet of messengers."},
            {"id": "3", "word": "THOUGH IT TARRY WAIT FOR IT", "clue": "Counsel when the appointed time seems delayed.", "verse": "Habakkuk 2:3", "verify": "though it tarry, wait for it", "summary": "Delay is not denial; the vision is for an appointed time."},
            {"id": "4", "word": "IT WILL SURELY COME", "clue": "Certainty of the vision’s fulfillment.", "verse": "Habakkuk 2:3", "verify": "it will surely come, it will not tarry", "summary": "Hope holds when calendars of men fail."},
            {"id": "5", "word": "THE JUST SHALL LIVE BY HIS FAITH", "clue": "Habakkuk’s line later quoted by Paul.", "verse": "Habakkuk 2:4", "verify": "the just shall live by his faith", "summary": "Righteousness by faith is the heartbeat of the remnant."},
        ],
    },
    {
        "id": "zephaniah-day",
        "title": "Zephaniah: Day of the Lord",
        "description": "Seek meekness before the day of the Lord’s anger.",
        "words": [
            {"id": "1", "word": "THE GREAT DAY OF THE LORD", "clue": "Zephaniah’s description of a day near and hasting greatly.", "verse": "Zephaniah 1:14", "verify": "The great day of the LORD is near", "summary": "The day of the Lord sobers every generation that hears."},
            {"id": "2", "word": "A DAY OF WRATH", "clue": "Part of Zephaniah’s catalog of that day’s terrors.", "verse": "Zephaniah 1:15", "verify": "That day is a day of wrath", "summary": "Judgment is real; mercy invites us before it falls."},
            {"id": "3", "word": "SEEK YE THE LORD", "clue": "Call to the meek of the earth before the decree bring forth.", "verse": "Zephaniah 2:3", "verify": "Seek ye the LORD, all ye meek of the earth", "summary": "Seeking God is the only safe path as the day approaches."},
            {"id": "4", "word": "SEEK RIGHTEOUSNESS SEEK MEEKNESS", "clue": "Twin pursuits that may hide in the day of anger.", "verse": "Zephaniah 2:3", "verify": "seek righteousness, seek meekness", "summary": "Character preparation cannot be borrowed at the last moment."},
            {"id": "5", "word": "IT MAY BE YE SHALL BE HID", "clue": "Conditional hope for those who seek in time.", "verse": "Zephaniah 2:3", "verify": "it may be ye shall be hid in the day of the LORD'S anger", "summary": "Hiding in Christ is the only shelter in the final storm."},
        ],
    },
    {
        "id": "matthew-signs",
        "title": "Matthew: Olivet Signs",
        "description": "Further signs from Jesus’ discourse on the Mount of Olives.",
        "words": [
            {"id": "1", "word": "THIS GOSPEL OF THE KINGDOM", "clue": "Must be preached in all the world before the end comes.", "verse": "Matthew 24:14", "verify": "this gospel of the kingdom shall be preached in all the world", "summary": "Mission finishes before history finishes."},
            {"id": "2", "word": "FOR A WITNESS UNTO ALL NATIONS", "clue": "Purpose of the global gospel proclamation.", "verse": "Matthew 24:14", "verify": "for a witness unto all nations", "summary": "Every nation must hear a fair testimony of Christ."},
            {"id": "3", "word": "THEN SHALL THE END COME", "clue": "What follows the finished witness of the gospel.", "verse": "Matthew 24:14", "verify": "and then shall the end come", "summary": "The end is tied to mission, not to human speculation alone."},
            {"id": "4", "word": "AS THE DAYS OF NOE WERE", "clue": "Jesus’ comparison for the coming of the Son of man.", "verse": "Matthew 24:37", "verify": "as the days of Noe were, so shall also the coming of the Son of man be", "summary": "Ordinary life continues until judgment suddenly closes the door."},
            {"id": "5", "word": "WATCH THEREFORE", "clue": "Jesus’ command because you know not what hour your Lord comes.", "verse": "Matthew 24:42", "verify": "Watch therefore: for ye know not what hour your Lord doth come", "summary": "Watchfulness is love awake to the nearness of Christ."},
        ],
    },
    {
        "id": "john-comfort",
        "title": "John: Comfort of the Spirit",
        "description": "Promise of the Comforter and truth that sanctifies.",
        "words": [
            {"id": "1", "word": "I WILL PRAY THE FATHER", "clue": "Jesus’ promise to request another Comforter for the disciples.", "verse": "John 14:16", "verify": "I will pray the Father, and he shall give you another Comforter", "summary": "The Spirit’s presence continues Christ’s ministry until He returns."},
            {"id": "2", "word": "SPIRIT OF TRUTH", "clue": "Title of the Comforter the world cannot receive.", "verse": "John 14:17", "verify": "Even the Spirit of truth", "summary": "Truth is a Person’s guidance, not mere information."},
            {"id": "3", "word": "HE WILL GUIDE YOU INTO ALL TRUTH", "clue": "Promise of the Spirit’s teaching work.", "verse": "John 16:13", "verify": "he will guide you into all truth", "summary": "Last-day light comes through Spirit-led Scripture."},
            {"id": "4", "word": "SANCTIFY THEM THROUGH THY TRUTH", "clue": "Jesus’ prayer for the disciples’ holiness.", "verse": "John 17:17", "verify": "Sanctify them through thy truth: thy word is truth", "summary": "Holiness is not emotion alone; the Word shapes character."},
            {"id": "5", "word": "THY WORD IS TRUTH", "clue": "Jesus’ definition of truth in His high-priestly prayer.", "verse": "John 17:17", "verify": "thy word is truth", "summary": "Scripture remains the standard when voices multiply."},
        ],
    },
    {
        "id": "acts-witness",
        "title": "Acts: Spirit-Powered Witness",
        "description": "Power after the Spirit comes; ends of the earth mission.",
        "words": [
            {"id": "1", "word": "YE SHALL RECEIVE POWER", "clue": "Promise after the Holy Ghost is come upon you.", "verse": "Acts 1:8", "verify": "ye shall receive power, after that the Holy Ghost is come upon you", "summary": "Latter rain power finishes the Acts 1:8 commission."},
            {"id": "2", "word": "WITNESSES UNTO ME", "clue": "What the disciples become in Jerusalem, Judea, Samaria, and beyond.", "verse": "Acts 1:8", "verify": "ye shall be witnesses unto me", "summary": "Witness is identity before it is strategy."},
            {"id": "3", "word": "UNTO THE UTTERMOST PART OF THE EARTH", "clue": "Geographic reach of the Spirit-powered commission.", "verse": "Acts 1:8", "verify": "unto the uttermost part of the earth", "summary": "No corner of earth is exempt from the gospel claim."},
            {"id": "4", "word": "THIS SAME JESUS", "clue": "Angels’ assurance about the manner of Christ’s return.", "verse": "Acts 1:11", "verify": "this same Jesus, which is taken up from you into heaven", "summary": "The returning Lord is the same Jesus who ascended."},
            {"id": "5", "word": "SHALL SO COME IN LIKE MANNER", "clue": "How Christ will return as the disciples watched Him go.", "verse": "Acts 1:11", "verify": "shall so come in like manner as ye have seen him go into heaven", "summary": "Literal, visible, personal return — not a secret spiritualization only."},
        ],
    },
    {
        "id": "romans-righteousness",
        "title": "Romans: Righteousness by Faith",
        "description": "Gospel power, no condemnation, and the law established by faith.",
        "words": [
            {"id": "1", "word": "I AM NOT ASHAMED OF THE GOSPEL", "clue": "Paul’s bold confession of the gospel’s power.", "verse": "Romans 1:16", "verify": "I am not ashamed of the gospel of Christ", "summary": "End-time witness needs unashamed courage."},
            {"id": "2", "word": "IT IS THE POWER OF GOD UNTO SALVATION", "clue": "What the gospel is to everyone that believes.", "verse": "Romans 1:16", "verify": "it is the power of God unto salvation", "summary": "Salvation is divine power applied to human need."},
            {"id": "3", "word": "THERE IS THEREFORE NOW NO CONDEMNATION", "clue": "Status of those in Christ Jesus.", "verse": "Romans 8:1", "verify": "There is therefore now no condemnation to them which are in Christ Jesus", "summary": "Judgment has an answer for those who abide in Christ."},
            {"id": "4", "word": "THE LAW IS HOLY", "clue": "Paul’s verdict on the commandment after the gospel is preached.", "verse": "Romans 7:12", "verify": "the law is holy, and the commandment holy, and just, and good", "summary": "Grace never makes the law sinful; it writes it on the heart."},
            {"id": "5", "word": "DO WE THEN MAKE VOID THE LAW", "clue": "Paul’s rhetorical question after teaching justification by faith.", "verse": "Romans 3:31", "verify": "Do we then make void the law through faith", "summary": "Faith establishes the law; it does not cancel it."},
        ],
    },
    {
        "id": "galatians-liberty",
        "title": "Galatians: Gospel Liberty",
        "description": "Christ living in me; liberty that serves love.",
        "words": [
            {"id": "1", "word": "I AM CRUCIFIED WITH CHRIST", "clue": "Paul’s confession of union with the crucified Lord.", "verse": "Galatians 2:20", "verify": "I am crucified with Christ", "summary": "Self dies so that Christ may live out His life in us."},
            {"id": "2", "word": "NEVERTHELESS I LIVE", "clue": "Paradox of the crucified believer who still lives.", "verse": "Galatians 2:20", "verify": "nevertheless I live; yet not I, but Christ liveth in me", "summary": "Christian life is Christ’s life reproduced by faith."},
            {"id": "3", "word": "THE LIFE WHICH I NOW LIVE", "clue": "How Paul lives in the flesh — by faith of the Son of God.", "verse": "Galatians 2:20", "verify": "the life which I now live in the flesh I live by the faith of the Son of God", "summary": "Daily faith, not a past memory, sustains holiness."},
            {"id": "4", "word": "STAND FAST THEREFORE IN THE LIBERTY", "clue": "Appeal not to be entangled again with the yoke of bondage.", "verse": "Galatians 5:1", "verify": "Stand fast therefore in the liberty wherewith Christ hath made us free", "summary": "Gospel liberty is freedom to obey from love, not license to sin."},
            {"id": "5", "word": "BY LOVE SERVE ONE ANOTHER", "clue": "How freedom expresses itself among believers.", "verse": "Galatians 5:13", "verify": "by love serve one another", "summary": "True liberty kneels to serve."},
        ],
    },
    {
        "id": "ephesians-unity",
        "title": "Ephesians: One Body",
        "description": "Unity of the Spirit and the church as Christ’s body.",
        "words": [
            {"id": "1", "word": "ONE LORD ONE FAITH ONE BAPTISM", "clue": "Threefold unity in Paul’s list for the church.", "verse": "Ephesians 4:5", "verify": "One Lord, one faith, one baptism", "summary": "Unity is grounded in Christ, not in compromise of truth."},
            {"id": "2", "word": "ENDEAVOURING TO KEEP THE UNITY", "clue": "How believers preserve the Spirit’s unity.", "verse": "Ephesians 4:3", "verify": "Endeavouring to keep the unity of the Spirit in the bond of peace", "summary": "Unity is kept by effort under the Spirit’s bond."},
            {"id": "3", "word": "SPEAKING THE TRUTH IN LOVE", "clue": "How the body grows up into Christ the head.", "verse": "Ephesians 4:15", "verify": "speaking the truth in love", "summary": "Last-day messages need both truth and love."},
            {"id": "4", "word": "GROW UP INTO HIM IN ALL THINGS", "clue": "Goal of church maturity under Christ the head.", "verse": "Ephesians 4:15", "verify": "may grow up into him in all things, which is the head, even Christ", "summary": "Maturity is measured by likeness to Christ."},
            {"id": "5", "word": "WE ARE HIS WORKMANSHIP", "clue": "Created in Christ Jesus unto good works.", "verse": "Ephesians 2:10", "verify": "we are his workmanship, created in Christ Jesus unto good works", "summary": "Grace produces works; works never purchase grace."},
        ],
    },
    {
        "id": "philippians-mind",
        "title": "Philippians: Mind of Christ",
        "description": "Humility, exaltation, and pressing toward the mark.",
        "words": [
            {"id": "1", "word": "LET THIS MIND BE IN YOU", "clue": "Paul’s call to share the attitude of Christ Jesus.", "verse": "Philippians 2:5", "verify": "Let this mind be in you, which was also in Christ Jesus", "summary": "The last generation needs the humility of the cross."},
            {"id": "2", "word": "HE HUMBLED HIMSELF", "clue": "Christ’s descent even to the death of the cross.", "verse": "Philippians 2:8", "verify": "he humbled himself, and became obedient unto death", "summary": "Obedience unto death is the path of the Lamb."},
            {"id": "3", "word": "GOD ALSO HATH HIGHLY EXALTED HIM", "clue": "Father’s response to the Son’s humiliation.", "verse": "Philippians 2:9", "verify": "God also hath highly exalted him", "summary": "The cross precedes the crown for Christ and His people."},
            {"id": "4", "word": "I PRESS TOWARD THE MARK", "clue": "Paul’s pursuit of the prize of the high calling.", "verse": "Philippians 3:14", "verify": "I press toward the mark for the prize of the high calling of God in Christ Jesus", "summary": "Sanctification is forward motion, not past achievement."},
            {"id": "5", "word": "MY GOD SHALL SUPPLY ALL YOUR NEED", "clue": "Promise through Christ Jesus according to His riches.", "verse": "Philippians 4:19", "verify": "my God shall supply all your need according to his riches in glory by Christ Jesus", "summary": "Provision for mission comes from heaven’s treasury."},
        ],
    },
    {
        "id": "colossians-christ",
        "title": "Colossians: Christ Supreme",
        "description": "Christ the Creator, the fullness of the Godhead, and hidden life.",
        "words": [
            {"id": "1", "word": "BY HIM WERE ALL THINGS CREATED", "clue": "Christ’s role in making heaven and earth.", "verse": "Colossians 1:16", "verify": "by him were all things created", "summary": "Creator Christ is worthy of the first angel’s worship call."},
            {"id": "2", "word": "HE IS BEFORE ALL THINGS", "clue": "Christ’s preeminence over creation.", "verse": "Colossians 1:17", "verify": "he is before all things, and by him all things consist", "summary": "History holds together only in Christ."},
            {"id": "3", "word": "IN HIM DWELLETH ALL THE FULNESS", "clue": "Fullness of the Godhead bodily in Christ.", "verse": "Colossians 2:9", "verify": "in him dwelleth all the fulness of the Godhead bodily", "summary": "We need no lesser mediator than the fullness of God in Christ."},
            {"id": "4", "word": "YE ARE COMPLETE IN HIM", "clue": "Status of believers who are in the head of all principality.", "verse": "Colossians 2:10", "verify": "ye are complete in him", "summary": "Completeness is in Christ, not in human additions to the gospel."},
            {"id": "5", "word": "YOUR LIFE IS HID WITH CHRIST IN GOD", "clue": "Security of the risen life with Christ.", "verse": "Colossians 3:3", "verify": "your life is hid with Christ in God", "summary": "When Christ appears, the hidden life will be revealed in glory."},
        ],
    },
    {
        "id": "thessalonians-hope",
        "title": "Thessalonians: Blessed Hope",
        "description": "Comfort of the resurrection and the day of the Lord.",
        "words": [
            {"id": "1", "word": "THE LORD HIMSELF SHALL DESCEND", "clue": "Personal descent of the Lord from heaven with a shout.", "verse": "1 Thessalonians 4:16", "verify": "the Lord himself shall descend from heaven with a shout", "summary": "The Advent is personal — the Lord Himself comes."},
            {"id": "2", "word": "THE DEAD IN CHRIST SHALL RISE FIRST", "clue": "Order of events at the trumpet of God.", "verse": "1 Thessalonians 4:16", "verify": "the dead in Christ shall rise first", "summary": "Graves cannot hold those who sleep in Jesus."},
            {"id": "3", "word": "CAUGHT UP TOGETHER WITH THEM", "clue": "Living saints join the raised ones in the clouds.", "verse": "1 Thessalonians 4:17", "verify": "caught up together with them in the clouds", "summary": "Family reunion in the air with the Lord forever."},
            {"id": "4", "word": "SO SHALL WE EVER BE WITH THE LORD", "clue": "Eternal outcome after the catching up.", "verse": "1 Thessalonians 4:17", "verify": "so shall we ever be with the Lord", "summary": "Heaven’s joy is perpetual presence with Christ."},
            {"id": "5", "word": "TO MEET THE LORD IN THE AIR", "clue": "Where living saints join the raised ones when Christ descends.", "verse": "1 Thessalonians 4:17", "verify": "to meet the Lord in the air", "summary": "Prophecy is for comfort as well as warning — reunion in the air with Christ forever."},
        ],
    },
    {
        "id": "timothy-scripture",
        "title": "Timothy: Scripture and Charge",
        "description": "Inspiration of Scripture and the charge to preach the word.",
        "words": [
            {"id": "1", "word": "ALL SCRIPTURE IS GIVEN BY INSPIRATION", "clue": "Paul’s doctrine of how Scripture comes from God.", "verse": "2 Timothy 3:16", "verify": "All scripture is given by inspiration of God", "summary": "Last-day faith rests on God-breathed Scripture."},
            {"id": "2", "word": "PROFITABLE FOR DOCTRINE", "clue": "First use Paul lists for inspired Scripture.", "verse": "2 Timothy 3:16", "verify": "profitable for doctrine, for reproof, for correction", "summary": "Doctrine must be Bible-derived, not tradition-driven."},
            {"id": "3", "word": "THAT THE MAN OF GOD MAY BE PERFECT", "clue": "Purpose of Scripture’s thorough equipment.", "verse": "2 Timothy 3:17", "verify": "That the man of God may be perfect, throughly furnished", "summary": "Scripture completes the worker for every good work."},
            {"id": "4", "word": "PREACH THE WORD", "clue": "Paul’s solemn charge to Timothy before God and Christ.", "verse": "2 Timothy 4:2", "verify": "Preach the word; be instant in season, out of season", "summary": "The loud cry is still the preached Word."},
            {"id": "5", "word": "THEY WILL NOT ENDURE SOUND DOCTRINE", "clue": "End-time itching ears that heap teachers to themselves.", "verse": "2 Timothy 4:3", "verify": "they will not endure sound doctrine", "summary": "Popularity is no test of truth in the last days."},
        ],
    },
    {
        "id": "hebrews-faith",
        "title": "Hebrews: Faith of the Fathers",
        "description": "Substance of things hoped for; looking unto Jesus.",
        "words": [
            {"id": "1", "word": "FAITH IS THE SUBSTANCE OF THINGS HOPED FOR", "clue": "Hebrews’ definition of faith.", "verse": "Hebrews 11:1", "verify": "faith is the substance of things hoped for", "summary": "Faith treats God’s promises as present reality."},
            {"id": "2", "word": "THE EVIDENCE OF THINGS NOT SEEN", "clue": "Second half of faith’s definition.", "verse": "Hebrews 11:1", "verify": "the evidence of things not seen", "summary": "Sight will confirm what faith already holds."},
            {"id": "3", "word": "WITHOUT FAITH IT IS IMPOSSIBLE TO PLEASE HIM", "clue": "Necessity of faith for anyone who comes to God.", "verse": "Hebrews 11:6", "verify": "without faith it is impossible to please him", "summary": "The remnant walks by faith when miracles multiply on both sides."},
            {"id": "4", "word": "LOOKING UNTO JESUS", "clue": "Author and finisher of our faith.", "verse": "Hebrews 12:2", "verify": "Looking unto Jesus the author and finisher of our faith", "summary": "Eyes on Jesus finish the race begun by grace."},
            {"id": "5", "word": "LET US RUN WITH PATIENCE", "clue": "The race set before us, laid aside every weight.", "verse": "Hebrews 12:1", "verify": "let us run with patience the race that is set before us", "summary": "Patience is the endurance of the saints in Revelation too."},
        ],
    },
    {
        "id": "james-works",
        "title": "James: Faith That Works",
        "description": "Doers of the word and pure religion before God.",
        "words": [
            {"id": "1", "word": "BE YE DOERS OF THE WORD", "clue": "James’ appeal not to be hearers only.", "verse": "James 1:22", "verify": "be ye doers of the word, and not hearers only", "summary": "Knowledge without obedience deceives the soul."},
            {"id": "2", "word": "FAITH WITHOUT WORKS IS DEAD", "clue": "James’ verdict on claim-only religion.", "verse": "James 2:26", "verify": "faith without works is dead also", "summary": "Living faith acts; empty profession does not save."},
            {"id": "3", "word": "PURE RELIGION AND UNDEFILED", "clue": "Visiting orphans and widows; keeping unspotted from the world.", "verse": "James 1:27", "verify": "Pure religion and undefiled before God and the Father is this", "summary": "True piety serves the vulnerable and stays unspotted."},
            {"id": "4", "word": "RESIST THE DEVIL", "clue": "James’ command so that the devil will flee.", "verse": "James 4:7", "verify": "Resist the devil, and he will flee from you", "summary": "Resistance under God’s submission ends Satan’s bluff."},
            {"id": "5", "word": "DRAW NIGH TO GOD", "clue": "Promise that God will draw nigh to you.", "verse": "James 4:8", "verify": "Draw nigh to God, and he will draw nigh to you", "summary": "Nearness to God is the safeguard of the last days."},
        ],
    },
    {
        "id": "peter-promise",
        "title": "Peter: Precious Promises",
        "description": "Partakers of the divine nature and a more sure word.",
        "words": [
            {"id": "1", "word": "EXCEEDING GREAT AND PRECIOUS PROMISES", "clue": "Given that we might be partakers of the divine nature.", "verse": "2 Peter 1:4", "verify": "exceeding great and precious promises", "summary": "Promises are the ladder of character growth."},
            {"id": "2", "word": "PARTAKERS OF THE DIVINE NATURE", "clue": "Result of claiming God’s promises by faith.", "verse": "2 Peter 1:4", "verify": "partakers of the divine nature", "summary": "Sanctification is sharing God’s life, not mere self-improvement."},
            {"id": "3", "word": "A MORE SURE WORD OF PROPHECY", "clue": "Peter’s confidence even above the mount of transfiguration vision.", "verse": "2 Peter 1:19", "verify": "We have also a more sure word of prophecy", "summary": "Prophetic Scripture outranks private experience."},
            {"id": "4", "word": "AS UNTO A LIGHT THAT SHINETH", "clue": "How prophecy functions in a dark place.", "verse": "2 Peter 1:19", "verify": "as unto a light that shineth in a dark place", "summary": "Prophecy lights the path until the day dawn."},
            {"id": "5", "word": "NO PROPHECY OF THE SCRIPTURE IS OF ANY PRIVATE INTERPRETATION", "clue": "Peter’s rule for handling prophetic Scripture.", "verse": "2 Peter 1:20", "verify": "no prophecy of the scripture is of any private interpretation", "summary": "Humble, Spirit-led interpretation guards against speculation."},
        ],
    },
    {
        "id": "john-love",
        "title": "John: Love and Commandments",
        "description": "Love perfected and commandments not grievous.",
        "words": [
            {"id": "1", "word": "GOD IS LOVE", "clue": "John’s simple revelation of God’s essential nature.", "verse": "1 John 4:8", "verify": "for God is love", "summary": "Every last-day doctrine must be read in the light of God’s love."},
            {"id": "2", "word": "WE LOVE HIM BECAUSE HE FIRST LOVED US", "clue": "Source of Christian love.", "verse": "1 John 4:19", "verify": "We love him, because he first loved us", "summary": "Obedience is response to love already given."},
            {"id": "3", "word": "THIS IS THE LOVE OF GOD", "clue": "That we keep His commandments.", "verse": "1 John 5:3", "verify": "this is the love of God, that we keep his commandments", "summary": "Love and law are not enemies in Scripture."},
            {"id": "4", "word": "HIS COMMANDMENTS ARE NOT GRIEVOUS", "clue": "John’s testimony about the weight of God’s commands.", "verse": "1 John 5:3", "verify": "his commandments are not grievous", "summary": "Grace makes the yoke easy and the burden light."},
            {"id": "5", "word": "HE THAT HATH THE SON HATH LIFE", "clue": "Eternal life defined by possession of the Son.", "verse": "1 John 5:12", "verify": "He that hath the Son hath life", "summary": "Life is a Person before it is a place."},
        ],
    },
    {
        "id": "jude-contend",
        "title": "Jude: Contend for the Faith",
        "description": "Earnest contention for the once-delivered faith.",
        "words": [
            {"id": "1", "word": "EARNESTLY CONTEND FOR THE FAITH", "clue": "Jude’s appeal for the faith once delivered unto the saints.", "verse": "Jude 1:3", "verify": "earnestly contend for the faith which was once delivered unto the saints", "summary": "Truth is worth earnest, loving contention."},
            {"id": "2", "word": "ONCE DELIVERED UNTO THE SAINTS", "clue": "The faith is not a modern invention.", "verse": "Jude 1:3", "verify": "the faith which was once delivered unto the saints", "summary": "Apostolic faith is the standard for the end-time church."},
            {"id": "3", "word": "BUILDING UP YOURSELVES ON YOUR MOST HOLY FAITH", "clue": "How to keep in the love of God while contending.", "verse": "Jude 1:20", "verify": "building up yourselves on your most holy faith", "summary": "Defense of truth requires personal spiritual construction."},
            {"id": "4", "word": "PRAYING IN THE HOLY GHOST", "clue": "Jude’s companion to building on holy faith.", "verse": "Jude 1:20", "verify": "praying in the Holy Ghost", "summary": "Prayer in the Spirit fuels faithful contention."},
            {"id": "5", "word": "KEEP YOURSELVES IN THE LOVE OF GOD", "clue": "Looking for the mercy of our Lord Jesus Christ unto eternal life.", "verse": "Jude 1:21", "verify": "Keep yourselves in the love of God", "summary": "Stay in love while you stand for truth."},
        ],
    },
    {
        "id": "rev-letters",
        "title": "Revelation: Letters to Churches",
        "description": "Further counsel from the seven letters.",
        "seasonId": "revelation",
        "words": [
            {"id": "1", "word": "I KNOW THY WORKS", "clue": "Christ’s repeated knowledge of each church’s condition.", "verse": "Revelation 2:2", "verify": "I know thy works", "summary": "Nothing about the church is hidden from its Head."},
            {"id": "2", "word": "BE THOU FAITHFUL UNTO DEATH", "clue": "Promise of a crown of life to Smyrna’s sufferers.", "verse": "Revelation 2:10", "verify": "be thou faithful unto death, and I will give thee a crown of life", "summary": "Faithfulness, not length of life, wins the crown."},
            {"id": "3", "word": "HOLD THAT FAST WHICH THOU HAST", "clue": "Counsel so that no man take thy crown.", "verse": "Revelation 3:11", "verify": "hold that fast which thou hast, that no man take thy crown", "summary": "Preserve present truth until Jesus comes."},
            {"id": "4", "word": "I STAND AT THE DOOR AND KNOCK", "clue": "Christ’s appeal outside Laodicea’s door.", "verse": "Revelation 3:20", "verify": "Behold, I stand at the door, and knock", "summary": "Even lukewarm hearts hear a personal knock of mercy."},
            {"id": "5", "word": "TO HIM THAT OVERCOMETH", "clue": "Repeated promise formula in the seven letters.", "verse": "Revelation 3:21", "verify": "To him that overcometh will I grant to sit with me in my throne", "summary": "Overcoming is possible in Christ for every church age."},
        ],
    },
    {
        "id": "rev-final",
        "title": "Revelation: Final Appeal",
        "description": "Last invitations and warnings of the Apocalypse.",
        "seasonId": "revelation",
        "words": [
            {"id": "1", "word": "BLESSED IS HE THAT READETH", "clue": "Opening beatitude of Revelation for readers and keepers.", "verse": "Revelation 1:3", "verify": "Blessed is he that readeth, and they that hear the words of this prophecy", "summary": "Prophetic study is commanded and blessed."},
            {"id": "2", "word": "KEEP THOSE THINGS WHICH ARE WRITTEN", "clue": "Blessing tied to keeping Revelation’s words.", "verse": "Revelation 1:3", "verify": "keep those things which are written therein", "summary": "Hearing without keeping forfeits the blessing."},
            {"id": "3", "word": "THE TIME IS AT HAND", "clue": "Urgency attached to Revelation’s opening blessing.", "verse": "Revelation 1:3", "verify": "for the time is at hand", "summary": "Urgency is part of the book’s message in every age."},
            {"id": "4", "word": "SURELY I COME QUICKLY", "clue": "Jesus’ thrice-echoed closing promise.", "verse": "Revelation 22:20", "verify": "Surely I come quickly", "summary": "The last word of Jesus in Scripture is soon return."},
            {"id": "5", "word": "EVEN SO COME LORD JESUS", "clue": "John’s response to the promise of soon coming.", "verse": "Revelation 22:20", "verify": "Even so, come, Lord Jesus", "summary": "The remnant’s prayer matches heaven’s promise."},
        ],
    },
    {
        "id": "psalms-refuge",
        "title": "Psalms: Refuge and Shepherd",
        "description": "Trust, shepherd care, and the word as lamp.",
        "words": [
            {"id": "1", "word": "THE LORD IS MY SHEPHERD", "clue": "Opening of the best-known psalm of trust.", "verse": "Psalm 23:1", "verify": "The LORD is my shepherd; I shall not want", "summary": "Shepherd care continues through the valley of the shadow."},
            {"id": "2", "word": "HE LEADETH ME BESIDE THE STILL WATERS", "clue": "Restoring path of the Shepherd for the soul.", "verse": "Psalm 23:2", "verify": "he leadeth me beside the still waters", "summary": "God’s leading is restful even in crisis seasons."},
            {"id": "3", "word": "THY WORD IS A LAMP UNTO MY FEET", "clue": "How Scripture guides step by step.", "verse": "Psalm 119:105", "verify": "Thy word is a lamp unto my feet, and a light unto my path", "summary": "Path light for the last days is still the Word."},
            {"id": "4", "word": "GOD IS OUR REFUGE AND STRENGTH", "clue": "A very present help in trouble.", "verse": "Psalm 46:1", "verify": "God is our refuge and strength, a very present help in trouble", "summary": "Refuge is a Person when the earth is removed."},
            {"id": "5", "word": "BE STILL AND KNOW THAT I AM GOD", "clue": "Command in the psalm of God’s exaltation among the nations.", "verse": "Psalm 46:10", "verify": "Be still, and know that I am God", "summary": "Stillness before God steadies the end-time heart."},
        ],
    },
    {
        "id": "proverbs-wisdom",
        "title": "Proverbs: Wisdom’s Call",
        "description": "Fear of the Lord and trust that does not lean on self.",
        "words": [
            {"id": "1", "word": "THE FEAR OF THE LORD IS THE BEGINNING OF WISDOM", "clue": "Foundation of true knowledge.", "verse": "Proverbs 9:10", "verify": "The fear of the LORD is the beginning of wisdom", "summary": "Reverence for God is the first lesson of true education."},
            {"id": "2", "word": "TRUST IN THE LORD WITH ALL THINE HEART", "clue": "Call not to lean on your own understanding.", "verse": "Proverbs 3:5", "verify": "Trust in the LORD with all thine heart", "summary": "Whole-heart trust is the remnant’s security system."},
            {"id": "3", "word": "LEAN NOT UNTO THINE OWN UNDERSTANDING", "clue": "Companion command to whole-heart trust.", "verse": "Proverbs 3:5", "verify": "lean not unto thine own understanding", "summary": "Self-wisdom fails in the final crisis."},
            {"id": "4", "word": "IN ALL THY WAYS ACKNOWLEDGE HIM", "clue": "Condition for God directing your paths.", "verse": "Proverbs 3:6", "verify": "In all thy ways acknowledge him, and he shall direct thy paths", "summary": "Direction follows acknowledgment in every path."},
            {"id": "5", "word": "THERE IS A WAY WHICH SEEMETH RIGHT", "clue": "Warning that ends in death.", "verse": "Proverbs 14:12", "verify": "There is a way which seemeth right unto a man, but the end thereof are the ways of death", "summary": "Seeming right is not the same as being right."},
        ],
    },
]


def normalize_answer(s: str) -> str:
    s = s.replace("\u2019", "'").replace("\u2018", "'").replace("'", "")
    s = re.sub(r"[^A-Za-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip().upper()


def load_pages() -> list[str]:
    if not KJV_PDF.exists():
        sys.exit(f"Missing {KJV_PDF}")
    return [(p.extract_text() or "") for p in PdfReader(str(KJV_PDF)).pages]


def normalize_pdf_text(text: str) -> str:
    text = text.replace("\u2019", "'").replace("\u2018", "'").replace("\ufffd", "'")
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)
    return re.sub(r"\s+", " ", text).strip()


def find_page(pages: list[str], needle: str) -> int | None:
    n = normalize_pdf_text(needle).lower()
    for i, text in enumerate(pages):
        if n in normalize_pdf_text(text).lower():
            return i + 1
    return None


def extract_snippet(pages: list[str], page: int, verify: str, max_len: int = 240) -> str:
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
    end = min(len(text), idx + max_len)
    snippet = text[start:end]
    snippet = re.sub(r"(\d)([A-Za-z])", r"\1 \2", snippet)
    snippet = re.sub(r"\s+", " ", snippet).strip()
    snippet = re.sub(r"^\d+\s+", "", snippet)
    if snippet and snippet[0].islower():
        parts = snippet.split(" ", 1)
        snippet = parts[1] if len(parts) == 2 and len(parts[0]) <= 5 else snippet[0].upper() + snippet[1:]
    return snippet


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")


def collect_existing() -> set[str]:
    texts = [
        WORDS_TS.read_text(encoding="utf-8"),
        EXPANSION_TS.read_text(encoding="utf-8") if EXPANSION_TS.exists() else "",
    ]
    words = set()
    for t in texts:
        words |= {normalize_answer(w) for w in re.findall(r"word:\s*['\"]([^'\"]+)['\"]", t)}
    return words


def build_entry(w: dict, pages: list[str], wid: str, existing: set[str]) -> dict:
    phrase = normalize_answer(w["word"])
    if phrase in existing:
        raise SystemExit(f"Duplicate word: {phrase} ({wid})")
    page = find_page(pages, w["verify"])
    if page is None:
        raise SystemExit(f"KJV verify failed for {wid}: {w['verify']!r}")
    # Prefer answer that is contiguous — verify answer in corpus loosely
    scripture = extract_snippet(pages, page, w["verify"])
    existing.add(phrase)
    return {
        "id": wid,
        "word": phrase,
        "clue": w["clue"],
        "verse": w["verse"],
        "scripture": scripture,
        "summary": w["summary"],
        "verify": w["verify"],
        "page": page,
    }


def apply_topups_to_words_ts(topup_entries: list[dict]) -> None:
    """Insert top-up word objects before the closing of each chapter's words array."""
    text = WORDS_TS.read_text(encoding="utf-8")
    for e in topup_entries:
        ch = e["id"].rsplit("-", 1)[0]
        # special chapter ids with hyphens
        for cand in (
            "time-of-trouble",
            "second-coming",
            "new-earth",
            "seal-of-god",
            "latter-rain",
            "loud-cry",
            "daniel-image",
            "daniel-beasts",
            "daniel-horn",
            "daniel-sanctuary",
            "daniel-stand",
            "rev-churches",
            "rev-seals",
            "rev-trumpets",
            "rev-beast",
            "rev-millennium",
        ):
            if e["id"].startswith(cand + "-"):
                ch = cand
                break
        if e["id"].startswith("signs-"):
            ch = "signs"
        if e["id"].startswith("shaking-"):
            ch = "shaking"
        if e["id"].startswith("judgment-"):
            ch = "judgment"
        if e["id"].startswith("deceptions-"):
            ch = "deceptions"

        block = (
            f"      {{\n"
            f'        id: "{e["id"]}",\n'
            f'        word: "{e["word"]}",\n'
            f'        clue: "{e["clue"].replace(chr(34), chr(92)+chr(34))}",\n'
            f'        verse: "{e["verse"]}",\n'
            f'        scripture: "{e["scripture"].replace(chr(34), chr(92)+chr(34))}",\n'
            f'        summary: "{e["summary"].replace(chr(34), chr(92)+chr(34))}"\n'
            f"      }}\n"
        )
        # Find chapter by id: "ch" and insert before last word's closing and chapter end
        # Insert before the `    ]` that closes words of this chapter
        # Pattern: id: "chapter" ... words: [ ... last entry ]
        marker = f'id: "{ch}"'
        idx = text.find(marker)
        if idx < 0:
            raise SystemExit(f"Chapter not found for top-up: {ch}")
        # find words array end after this chapter start — first `    ]\n  }` after idx
        words_start = text.find("words: [", idx)
        # find matching close of words array at chapter level — search for `\n    ]\n  }` after words_start
        close = text.find("\n    ]\n  }", words_start)
        if close < 0:
            close = text.find("\n    ]\n  },", words_start)
        if close < 0:
            raise SystemExit(f"Could not find words array close for {ch}")
        # ensure previous entry has comma
        before = text[:close]
        # last non-ws
        strip_end = before.rstrip()
        if not strip_end.endswith(","):
            # add comma after last }
            last_brace = strip_end.rfind("}")
            before = strip_end[: last_brace + 1] + "," + strip_end[last_brace + 1 :]
            # keep following whitespace from original roughly
            text = before + text[close:]
            close = text.find("\n    ]\n  }", words_start)
            if close < 0:
                close = text.find("\n    ]\n  },", words_start)
        insertion = "\n" + block.rstrip() + ","
        text = text[:close] + insertion + text[close:]
        print(f"  top-up inserted: {e['id']}")
    WORDS_TS.write_text(text, encoding="utf-8")


def main() -> None:
    pages = load_pages()
    existing = collect_existing()
    print(f"existing words: {len(existing)}")

    ledger = []
    expert = {}
    topup_built = []

    print("Building top-ups...")
    for t in TOPUPS:
        e = build_entry(t, pages, t["id"], existing)
        topup_built.append(e)
        ledger.append(
            {
                "id": e["id"],
                "word": e["word"],
                "verse": e["verse"],
                "verify_substring": e["verify"],
                "kjv_pdf_page": e["page"],
                "grade": "VERIFIED",
                "kind": "topup",
                "source": KJV_PDF.name,
            }
        )
        expert[e["id"]] = f"{e['verse']} — {e['verify'][:60]}"

    print("Building new chapters...")
    chapters_out = []
    for ch in NEW_CHAPTERS:
        ch_words = []
        for w in ch["words"]:
            wid = f"{ch['id']}-{w['id']}"
            e = build_entry(w, pages, wid, existing)
            ch_words.append(e)
            ledger.append(
                {
                    "id": e["id"],
                    "word": e["word"],
                    "verse": e["verse"],
                    "verify_substring": e["verify"],
                    "kjv_pdf_page": e["page"],
                    "grade": "VERIFIED",
                    "kind": "new-chapter",
                    "source": KJV_PDF.name,
                }
            )
            expert[e["id"]] = f"{e['verse']} — {e['verify'][:60]}"
        chapters_out.append(
            {
                "id": ch["id"],
                "title": ch["title"],
                "description": ch["description"],
                "seasonId": ch.get("seasonId"),
                "words": ch_words,
            }
        )

    if len(ledger) != 150:
        raise SystemExit(f"Expected 150, got {len(ledger)}")

    # Write expansion2 TS
    lines = [
        'import type { Chapter } from "./words";',
        "",
        "/** 130 KJV-verified batch-2 chapters (2026-07-10) + top-ups live in words.ts. */",
        "export const expansionChapters2: Chapter[] = [",
    ]
    for ch in chapters_out:
        lines.append("  {")
        lines.append(f"    id: '{esc(ch['id'])}',")
        lines.append(f"    title: '{esc(ch['title'])}',")
        lines.append(f"    description: '{esc(ch['description'])}',")
        if ch.get("seasonId"):
            lines.append(f"    seasonId: '{esc(ch['seasonId'])}',")
        lines.append("    words: [")
        for w in ch["words"]:
            lines.append("      {")
            lines.append(f"        id: '{esc(w['id'])}',")
            lines.append(f"        word: '{esc(w['word'])}',")
            lines.append(f"        clue: '{esc(w['clue'])}',")
            lines.append(f"        verse: '{esc(w['verse'])}',")
            lines.append(f"        scripture: '{esc(w['scripture'])}',")
            lines.append(f"        summary: '{esc(w['summary'])}'")
            lines.append("      },")
        lines.append("    ]")
        lines.append("  },")
    lines.append("];")
    lines.append("")
    OUT_TS.write_text("\n".join(lines), encoding="utf-8")

    elines = [
        "/** Expert clues for batch-2 expansion (and top-ups). */",
        "export const expertClueExpansion2: Record<string, string> = {",
    ]
    for k, v in expert.items():
        elines.append(f"  '{esc(k)}': '{esc(v)}',")
    elines.append("};")
    elines.append("")
    OUT_EXPERT.write_text("\n".join(elines), encoding="utf-8")

    OUT_LEDGER.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_TS}")
    print(f"Wrote {OUT_EXPERT}")
    print(f"Wrote {OUT_LEDGER}")

    print("Applying top-ups to words.ts...")
    apply_topups_to_words_ts(topup_built)
    print("Done.")


if __name__ == "__main__":
    main()
