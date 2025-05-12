"""
Legal Terms Database

This module contains a comprehensive dictionary of legal terms and their explanations.
These terms will be used to populate the database with legal jargon entries.
"""

# Dictionary of legal terms with their explanations
LEGAL_TERMS = {
    "a fortiori": {
        "simple_explanation": "This means 'with stronger reason.' It's used when an argument applies even more strongly in a second case than it did in a previously accepted case.",
        "fun_explanation": "It's like saying 'If I can lift 100 pounds, then I can definitely lift 50 pounds!' The second conclusion is even more obvious than the first.",
        "cartoon_description": "A cartoon showing a judge lifting a tiny weight labeled '50lbs' with one finger after bench pressing a massive barbell labeled '100lbs'."
    },
    "ab initio": {
        "simple_explanation": "A Latin term meaning 'from the beginning' or 'from inception.' It refers to something being the case from the start.",
        "fun_explanation": "It's the legal way of saying 'broken since birth.' Like a cake that someone forgot to add eggs to - it was doomed from the start!",
        "cartoon_description": "A cartoon of a contract with a birth certificate showing it was born with problems, with a doctor saying 'I'm sorry, it's void ab initio'."
    },
    "actus reus": {
        "simple_explanation": "The 'guilty act' component of a crime—the physical action that the law prohibits, as opposed to the mental state (mens rea).",
        "fun_explanation": "Think of it as the 'caught in the act' part of crime. It's what security cameras catch you doing, not what's going on in your head!",
        "cartoon_description": "A cartoon showing a person's body stealing a cookie jar (labeled 'actus reus') while their brain (labeled 'mens rea') thinks mischievous thoughts."
    },
    "affidavit": {
        "simple_explanation": "A written statement confirmed by oath or affirmation for use as evidence in court.",
        "fun_explanation": "It's like pinky-promising on paper with the added bonus that lying gets you in trouble with the law, not just your friends.",
        "cartoon_description": "A cartoon showing a person with their hand on a stack of papers instead of a Bible, with a thought bubble saying 'I swear this is what happened... honestly!'"
    },
    "amicus curiae": {
        "simple_explanation": "Latin for 'friend of the court.' A person or organization that is not a party to a case but provides information to assist the court.",
        "fun_explanation": "It's like when you're arguing with your sibling and your cousin jumps in with 'Actually, I saw what happened...' They're not directly involved but want to help sort things out.",
        "cartoon_description": "A cartoon of a judge in a courtroom with a person peeking through the window holding a sign saying 'I have some helpful information!'"
    },
    "arraignment": {
        "simple_explanation": "A court proceeding where a person accused of a crime is brought before a judge, informed of the charges, and asked to enter a plea.",
        "fun_explanation": "It's the legal version of 'we need to talk about what you did,' except it happens in a fancy room and everyone's wearing serious clothes.",
        "cartoon_description": "A cartoon of a nervous-looking defendant standing before a stern judge who's reading a long list while asking 'So, did you do it or not?'"
    },
    "bail": {
        "simple_explanation": "Money or property given to the court to secure a defendant's temporary release from jail and ensure they return for trial.",
        "fun_explanation": "It's like leaving your driver's license with the bowling alley when you rent shoes - a deposit that says 'Don't worry, I'll be back!'",
        "cartoon_description": "A cartoon showing a person handing over a giant bag of money labeled 'BAIL' while attached to it is a string that connects to the courthouse."
    },
    "bench trial": {
        "simple_explanation": "A trial where a judge alone, without a jury, decides the facts and applies the law to reach a verdict.",
        "fun_explanation": "It's like playing a game where one person is both the referee and the scorekeeper—the judge makes all the calls!",
        "cartoon_description": "A cartoon showing a judge wearing multiple hats labeled 'Fact Finder,' 'Law Applier,' and 'Decision Maker' while a confused defendant watches."
    },
    "burden of proof": {
        "simple_explanation": "The obligation to prove one's assertion in court, typically resting on the party who initiates the claim.",
        "fun_explanation": "It's like when your mom says 'If you're claiming your sister ate the last cookie, you better have evidence!' The accuser needs to back up their story.",
        "cartoon_description": "A cartoon of a person struggling to carry a heavy backpack labeled 'PROOF' up a steep hill toward a courthouse on top."
    },
    "certiorari": {
        "simple_explanation": "A writ issued by a higher court to review a decision of a lower court.",
        "fun_explanation": "It's the Supreme Court's way of saying 'Hold up, we want to take a second look at this case!' It's the legal equivalent of calling for an instant replay.",
        "cartoon_description": "A cartoon of nine Supreme Court justices holding a giant magnifying glass over a tiny lower court decision paper."
    },
    "civil law": {
        "simple_explanation": "The branch of law dealing with disputes between individuals or organizations, where compensation may be awarded to the victim.",
        "fun_explanation": "It's playground justice for adults—'You broke my toy (or contract), so now you have to give me money to make it right!'",
        "cartoon_description": "A cartoon showing two people in business suits playing tug-of-war with a dollar sign, with a judge in the middle holding a whistle."
    },
    "common law": {
        "simple_explanation": "Law developed through judges' decisions in court and through legal precedent, as opposed to laws enacted by legislatures.",
        "fun_explanation": "It's like following the rules of a game that were never officially written down, but everyone agrees 'that's how we've always played it!'",
        "cartoon_description": "A cartoon showing old judges passing a thick book labeled 'THE RULES' to younger judges, with sticky notes and handwritten edits all over it."
    },
    "contempt of court": {
        "simple_explanation": "Disobeying a court order or showing disrespect for the court's authority in the courtroom.",
        "fun_explanation": "It's what happens when you ignore the judge's rules—like getting detention, but for grown-ups, and possibly with jail time!",
        "cartoon_description": "A cartoon of a judge banging their gavel while yelling at a person who is on their phone, sleeping, or making faces during court."
    },
    "corpus delicti": {
        "simple_explanation": "The 'body of the crime' - the facts showing that a crime has been committed, not just the physical body in murder cases.",
        "fun_explanation": "It's like needing proof the cookie jar was actually raided before accusing someone of stealing cookies—you need evidence a crime happened before blaming someone.",
        "cartoon_description": "A cartoon showing a detective pointing to an empty cookie jar saying 'We have corpus delicti!' while ignoring the person with crumbs all over their face."
    },
    "damages": {
        "simple_explanation": "Money awarded by a court to a person who has been injured or suffered loss because of the wrongful conduct of another party.",
        "fun_explanation": "It's the adult version of 'you break it, you buy it' - except sometimes you pay extra for the emotional distress of breaking someone's favorite vase!",
        "cartoon_description": "A cartoon of a judge handing a person with a broken arm a giant check while pointing sternly at another person hiding a baseball bat."
    },
    "de facto": {
        "simple_explanation": "Latin for 'in fact.' It refers to situations that exist in reality, even if not officially recognized by law.",
        "fun_explanation": "It's like when your friend's cat lives at your place and uses your litter box—it's not officially your cat, but in reality (de facto), it kind of is!",
        "cartoon_description": "A cartoon showing a person sitting on a throne wearing a paper crown, while a sign reads 'Not the official king (but everyone listens to him anyway).'"
    },
    "de jure": {
        "simple_explanation": "Latin for 'by law.' It refers to conditions that are according to law or by official or legal right.",
        "fun_explanation": "It's the 'on paper' reality - like when you're technically the owner of a car that your teenager drives exclusively. De jure it's yours; de facto it's theirs!",
        "cartoon_description": "A cartoon showing a tiny crown sitting on a lawbook labeled 'de jure ruler,' while the actual king sits elsewhere on the throne."
    },
    "deposition": {
        "simple_explanation": "Out-of-court testimony given under oath by a witness and recorded for later use in court or discovery.",
        "fun_explanation": "It's like a pre-interview for the big court show, except everything you say can and will be used against you (or for you) when the real performance starts!",
        "cartoon_description": "A cartoon of a nervous witness speaking while a lawyer records every word, with thought bubbles showing the witness carefully choosing each word."
    },
    "discovery": {
        "simple_explanation": "The pre-trial phase where each party can request evidence and information from the other side.",
        "fun_explanation": "It's like when you and your sibling both have to empty your pockets and show what you're hiding before mom decides who started the fight!",
        "cartoon_description": "A cartoon showing two lawyers exchanging giant folders labeled 'SECRETS,' while both looking upset about having to share."
    },
    "double jeopardy": {
        "simple_explanation": "A legal principle that prevents a person from being tried twice for the same crime following a valid acquittal or conviction.",
        "fun_explanation": "It's the legal version of 'no takebacks' - once the court says you're not guilty, they can't change their mind later!",
        "cartoon_description": "A cartoon showing a person walking out of court with a 'NOT GUILTY' sign, while a frustrated prosecutor tries to pull them back saying 'Wait! I found new evidence!'"
    },
    "due process": {
        "simple_explanation": "The legal requirement that the state must respect all legal rights owed to a person, ensuring fair treatment through the judicial system.",
        "fun_explanation": "It's like the rules of fair play in the legal game - the government can't just change the rules halfway through or skip important steps to win!",
        "cartoon_description": "A cartoon showing Lady Justice holding up a checklist of procedural steps that must be followed, blocking an impatient police officer trying to skip to the end."
    },
    "en banc": {
        "simple_explanation": "When all judges of a court hear a case together, rather than the normal panel of just a few judges.",
        "fun_explanation": "It's the 'all hands on deck' approach to judging - like calling in the entire family for a difficult decision instead of just asking Dad!",
        "cartoon_description": "A cartoon showing a tiny defendant facing a massive bench filled with dozens of judges all wearing identical robes and expressions."
    },
    "escrow": {
        "simple_explanation": "A third-party arrangement where funds or assets are held until specified conditions are met.",
        "fun_explanation": "It's like asking your trustworthy friend to hold onto concert tickets and money until your other friend delivers the backstage passes they promised!",
        "cartoon_description": "A cartoon showing a neutral-looking banker standing between two people, holding a bag of money and a house key, saying 'Nobody gets anything until all the paperwork is done!'"
    },
    "ex parte": {
        "simple_explanation": "A legal proceeding brought by one person in the absence of and without representation or notification of other parties.",
        "fun_explanation": "It's like having a private chat with the teacher about a group project when your teammates aren't around - a one-sided conversation!",
        "cartoon_description": "A cartoon of a judge and one lawyer whispering behind a hand while the chair for the other party sits conspicuously empty."
    },
    "felony": {
        "simple_explanation": "A serious crime that typically carries a punishment of imprisonment for more than one year or even death.",
        "fun_explanation": "It's the 'you're in big trouble' category of crimes - not a minor oops but a major 'this is going to seriously impact your life' offense!",
        "cartoon_description": "A cartoon showing crime severity as a meter ranging from 'Parking Ticket' to 'Felony,' with the needle deep in the red 'Felony' zone."
    },
    "force majeure": {
        "simple_explanation": "Unforeseeable circumstances that prevent someone from fulfilling a contract, often used as a clause to remove liability.",
        "fun_explanation": "It's the legal way of saying 'Not my fault! Blame the hurricane/pandemic/alien invasion!' when you can't keep your contractual promises.",
        "cartoon_description": "A cartoon showing a person shrugging while pointing to a tornado, flood, and meteor shower happening simultaneously, with a torn contract floating away."
    },
    "fruit of the poisonous tree": {
        "simple_explanation": "Legal evidence that was obtained illegally and therefore cannot be used in court.",
        "fun_explanation": "It's like saying 'you can't use those cookies in the bake sale because you stole the recipe!' If you got it through illegal means, you can't use what you found.",
        "cartoon_description": "A cartoon of a police officer picking evidence-apples from a tree with 'ILLEGAL SEARCH' written on its trunk, while a judge with scissors cuts the evidence out of their hands."
    },
    "grand jury": {
        "simple_explanation": "A group of citizens who are presented with evidence by a prosecutor to determine if there's probable cause to indict someone for a crime.",
        "fun_explanation": "It's like a preview panel that decides if a case is juicy enough to go to the big show - they don't decide guilt, just whether there's enough evidence to have a trial!",
        "cartoon_description": "A cartoon showing a group of jurors examining evidence through magnifying glasses, while giving a thumbs up or down on whether the case goes forward."
    },
    "guardian ad litem": {
        "simple_explanation": "A court-appointed individual who investigates and represents the best interests of a child or incapacitated adult in legal proceedings.",
        "fun_explanation": "It's like having a special advocate who stands up for you when you can't effectively speak for yourself - your very own legal superhero!",
        "cartoon_description": "A cartoon showing a caped figure standing protectively between a child and complicated legal proceedings, holding a shield that says 'BEST INTERESTS.'"
    },
    "habeas corpus": {
        "simple_explanation": "A legal action that demands that a public official deliver an imprisoned person to the court and show a valid reason for their detention.",
        "fun_explanation": "Latin for 'you have the body.' It's like saying to the jailer: 'Show me the person and prove why they're in timeout, or let them go!'",
        "cartoon_description": "A cartoon showing a judge looking at a jailer saying 'Either show me why this person is in jail, or set them free!' with the person looking hopeful."
    },
    "hearsay": {
        "simple_explanation": "Testimony from a witness who relates not what they personally experienced, but what others have said.",
        "fun_explanation": "The legal equivalent of 'my friend told me that her cousin's neighbor said...' - generally not allowed unless it fits one of many exceptions!",
        "cartoon_description": "A cartoon showing people playing telephone/Chinese whispers game in court with the message getting more ridiculous with each person."
    },
    "indictment": {
        "simple_explanation": "A formal accusation that a person has committed a crime, typically decided by a grand jury.",
        "fun_explanation": "It's the legal equivalent of a group of your neighbors agreeing 'Yeah, there's enough evidence here that we should probably have a serious conversation about what you did!'",
        "cartoon_description": "A cartoon showing a person receiving a fancy envelope with a wax seal, looking nervous as they read 'You're formally invited... to your own criminal trial.'"
    },
    "injunction": {
        "simple_explanation": "A court order that prevents a person or entity from beginning or continuing an action.",
        "fun_explanation": "It's like the legal version of a parent saying 'Stop that right now!' - a judge's way of hitting the pause button on something they think might cause harm.",
        "cartoon_description": "A cartoon of a giant hand labeled 'COURT' holding a stop sign in front of a person about to take an action, with the person frozen mid-step."
    },
    "in limine": {
        "simple_explanation": "A motion made before trial begins to exclude evidence from the proceedings.",
        "fun_explanation": "It's the pre-game strategy session where lawyers try to get the referee (judge) to ban certain plays before the game even starts!",
        "cartoon_description": "A cartoon showing lawyers in a huddle before trial, with one holding up evidence in a box labeled 'DO NOT OPEN IN COURT' while the judge considers it."
    },
    "ipso facto": {
        "simple_explanation": "Latin for 'by the fact itself.' It indicates that something is a direct consequence of the facts.",
        "fun_explanation": "It's the 'well, duh!' of legal Latin. If you stay out all night in the rain, ipso facto, you'll be wet and tired the next day!",
        "cartoon_description": "A cartoon showing a person pointing to obvious cause and effect, like someone standing in rain (cause) connected by a straight line to being soaking wet (effect)."
    },
    "jurisdiction": {
        "simple_explanation": "The official power to make legal decisions and judgments within a defined territory or over certain types of legal cases.",
        "fun_explanation": "It's like the boundary lines on a sports field - step outside your court's territory, and your ruling doesn't count anymore!",
        "cartoon_description": "A cartoon showing a judge stopping at a line on the ground labeled 'END OF JURISDICTION' while their gavel power disappears as they cross it."
    },
    "laches": {
        "simple_explanation": "A defense against a claim that was not made within a reasonable time, causing disadvantage to the opposing party.",
        "fun_explanation": "It's the legal version of 'You snooze, you lose!' If you wait too long to complain about something, the court might tell you it's too late!",
        "cartoon_description": "A cartoon of a person finally arriving at court with a complaint, only to find cobwebs on the judge and a calendar showing years have passed."
    },
    "mens rea": {
        "simple_explanation": "The mental element of a crime—the intent or knowledge of wrongdoing that constitutes part of a crime, as opposed to the action itself (actus reus).",
        "fun_explanation": "It's the 'guilty mind' part of a crime—did you accidentally knock over that vase (oops!) or did you plan to smash it all along (mwahaha!)?",
        "cartoon_description": "A cartoon of a brain wearing a devil costume or angel costume, representing the mental state behind an action."
    },
    "miranda rights": {
        "simple_explanation": "The rights that police must read to a suspect before questioning, including the right to remain silent and the right to an attorney.",
        "fun_explanation": "It's that speech from crime shows: 'You have the right to remain silent...' - the legal version of 'anything you say can and will be used to get you in trouble!'",
        "cartoon_description": "A cartoon showing a police officer reading from a card to a surprised suspect, with a speech bubble containing the familiar Miranda warning."
    },
    "moot": {
        "simple_explanation": "Referring to an issue that has no practical significance or is hypothetical, especially a legal question that has no current controversy.",
        "fun_explanation": "It's like arguing about who should have done the dishes after they've already been washed - a debate that doesn't matter anymore because circumstances have changed!",
        "cartoon_description": "A cartoon showing lawyers passionately arguing in court while the subject of their dispute has already disappeared or been resolved."
    },
    "negligence": {
        "simple_explanation": "Failure to take proper care in doing something, resulting in damage or injury to another.",
        "fun_explanation": "It's when you should have known better - like leaving a banana peel on the floor when any cartoon has taught you someone will slip on it!",
        "cartoon_description": "A cartoon showing a person texting while walking, about to step into an open manhole that has no warning signs or barriers."
    },
    "nolo contendere": {
        "simple_explanation": "Latin for 'I do not wish to contend.' A plea where the defendant doesn't admit guilt but accepts punishment.",
        "fun_explanation": "It's like telling mom 'I'm not saying I ate the cookies, but I'll accept the punishment anyway' - a way to take the consequences without admitting you did it!",
        "cartoon_description": "A cartoon showing a person with hands up saying 'I'm not saying I did it!' while simultaneously reaching for the punishment paperwork with their other hand."
    },
    "nuisance": {
        "simple_explanation": "Something that interferes with a person's enjoyment of their property or endangers life, health, or property.",
        "fun_explanation": "It's the legal word for 'that thing your neighbor does that drives you crazy' - like playing the drums at 3 AM or letting their tree drop all its leaves in your pool!",
        "cartoon_description": "A cartoon showing a person trying to relax while surrounded by various annoyances - loud music, smelly garbage, a neighbor's tree branches, etc."
    },
    "objection": {
        "simple_explanation": "A formal protest raised during a legal proceeding to call the court's attention to testimony or evidence that may be improper.",
        "fun_explanation": "It's the lawyer's version of yelling 'That's not fair!' during a game - a way to challenge something that breaks the rules of the court!",
        "cartoon_description": "A cartoon of a lawyer dramatically jumping up from their chair pointing skyward yelling 'OBJECTION!' while everyone else looks startled."
    },
    "per curiam": {
        "simple_explanation": "Latin for 'by the court.' A legal opinion issued by an appellate court as a whole, not signed by an individual judge.",
        "fun_explanation": "It's like getting a group email from all your professors at once - nobody takes individual credit or blame, it's from 'The Court' collectively!",
        "cartoon_description": "A cartoon showing multiple judges hiding behind one giant mask labeled 'THE COURT' while handing down a decision."
    },
    "plea bargain": {
        "simple_explanation": "An agreement in a criminal case where a defendant pleads guilty to a lesser charge in exchange for a more lenient sentence.",
        "fun_explanation": "It's the legal equivalent of 'I'll admit to eating one cookie if you don't tell Mom I actually ate the whole jar' - a compromise to avoid the worst outcome!",
        "cartoon_description": "A cartoon showing a prosecutor and defendant at a bargaining table, with the prosecutor removing blocks from a tower labeled 'Charges' while the defendant nods."
    },
    "precedent": {
        "simple_explanation": "A previously decided court case that establishes a principle used to decide later similar cases.",
        "fun_explanation": "It's the 'we've already been through this before' rule - like when your younger sibling asks for something your parents already decided on with you!",
        "cartoon_description": "A cartoon showing a judge pointing to a tall stack of old cases saying 'See? We already decided this 50 years ago!' while a lawyer looks disappointed."
    },
    "prima facie": {
        "simple_explanation": "Latin for 'at first sight.' Evidence that is sufficient to establish a fact or case unless contradicted.",
        "fun_explanation": "It's like when you walk into the kitchen and see your kid with chocolate all over their face - it looks like they ate the cake without needing further investigation!",
        "cartoon_description": "A cartoon showing a judge looking at obvious evidence (like fingerprints at a crime scene) saying 'Well, this certainly LOOKS like a case!'"
    },
    "pro bono": {
        "simple_explanation": "Legal work performed voluntarily and without payment, often for the public good.",
        "fun_explanation": "It's when a lawyer says 'This one's on the house' - they're working for free because they believe in the cause or want to help someone who can't afford legal help!",
        "cartoon_description": "A cartoon showing a lawyer with angel wings helping a client while tearing up a bill marked with dollar signs."
    },
    "pro se": {
        "simple_explanation": "Representing yourself in court without a lawyer.",
        "fun_explanation": "It's like being the coach AND star player of your own legal team!",
        "cartoon_description": "A cartoon of a person wearing half a business suit and half a judge's robe, pointing to a legal book while saying 'I got this!'"
    },
    "prosecutor": {
        "simple_explanation": "A legal official who initiates and presents criminal cases against individuals accused of crimes.",
        "fun_explanation": "They're the opposing player in the courtroom game - their job is to convince the jury that you broke the rules and deserve a penalty!",
        "cartoon_description": "A cartoon showing a serious-looking attorney pointing at evidence and then at a nervous defendant, with 'The People's Case' written on their briefcase."
    },
    "quash": {
        "simple_explanation": "To reject or void, especially to make a court order invalid.",
        "fun_explanation": "It's the legal version of 'cancel that' - like hitting the delete button on an order or subpoena that shouldn't have been issued!",
        "cartoon_description": "A cartoon showing a judge dramatically stamping 'CANCELLED' on a legal document while the paper makes a 'quashing' sound effect."
    },
    "quid pro quo": {
        "simple_explanation": "Latin for 'something for something.' An exchange of goods, services, or favors of roughly equal value.",
        "fun_explanation": "It's the 'You scratch my back, I'll scratch yours' of legal Latin - a trading of favors or benefits where both sides get something they want!",
        "cartoon_description": "A cartoon showing two people exchanging packages across a table, each with thought bubbles showing they think they're getting the better deal."
    },
    "reasonable doubt": {
        "simple_explanation": "The standard of proof required to convict a criminal defendant, requiring that no reasonable person could doubt the defendant's guilt.",
        "fun_explanation": "It's stronger than 'probably did it' but less than 'absolutely 100% certain' - like being sure enough that you'd bet your paycheck, but maybe not your house!",
        "cartoon_description": "A cartoon showing a scale of certainty from 'Maybe' to 'Beyond Reasonable Doubt' to 'Absolutely Certain' with a criminal conviction threshold at 'Beyond Reasonable Doubt.'"
    },
    "recuse": {
        "simple_explanation": "To remove oneself as a judge or juror in a legal case due to potential bias or conflict of interest.",
        "fun_explanation": "It's like saying 'I better not judge this cookie-stealing case since the suspect is my kid' - stepping aside when you can't be fair!",
        "cartoon_description": "A cartoon showing a judge stepping down from the bench after recognizing the defendant as their golf buddy or next-door neighbor."
    },
    "res ipsa loquitur": {
        "simple_explanation": "Latin for 'the thing speaks for itself.' A doctrine that presumes negligence from the very nature of an accident or injury.",
        "fun_explanation": "It's when the evidence is so obvious that it's like the smoking gun is actually still smoking! No further explanation needed!",
        "cartoon_description": "A cartoon showing a falling piano about to hit someone with a lawyer pointing and saying 'I think we can all see what happened here!'"
    },
    "res judicata": {
        "simple_explanation": "A matter that has been decided by a court and may not be pursued further by the same parties.",
        "fun_explanation": "It's the legal way of saying 'we already answered this question, so stop asking!' - preventing people from trying the same case over and over hoping for a different result.",
        "cartoon_description": "A cartoon showing a judge stamping 'CASE CLOSED - FOREVER' on a file while a persistent lawyer tries to reopen it."
    },
    "restraining order": {
        "simple_explanation": "A court order prohibiting a person from taking certain actions or approaching/contacting specified people.",
        "fun_explanation": "It's a legal forcefield that says 'you must stay THIS far away' - the court's way of creating boundaries when people won't respect them voluntarily!",
        "cartoon_description": "A cartoon showing a person unable to cross an invisible line around another person, with a paper labeled 'RESTRAINING ORDER' creating a barrier between them."
    },
    "retainer": {
        "simple_explanation": "An upfront fee paid to secure a lawyer's services, often before any specific work is required.",
        "fun_explanation": "It's like putting a lawyer on speed-dial - you pay upfront to make sure they'll answer when you call, even if you don't need them right now!",
        "cartoon_description": "A cartoon showing a client handing money to a lawyer who is putting a 'RESERVED' sign on their time calendar."
    },
    "sanction": {
        "simple_explanation": "A penalty for disobeying a law or rule, or official permission for an action.",
        "fun_explanation": "As a penalty, it's the legal equivalent of a time-out for adults - a punishment for not following the rules! As permission, it's the official thumbs-up to proceed.",
        "cartoon_description": "A cartoon showing a dual image: on one side a judge imposing a fine on someone looking guilty, on the other side the judge giving an approval stamp to a happy applicant."
    },
    "service of process": {
        "simple_explanation": "The formal delivery of legal documents that notify a person of a legal action against them.",
        "fun_explanation": "It's the 'You've been invited to a court party!' moment - except it's not a party, and you really need to show up, or decisions will be made without you!",
        "cartoon_description": "A cartoon of a process server chasing someone trying to avoid receiving papers, with the papers dramatically flying through the air."
    },
    "settlement": {
        "simple_explanation": "An agreement resolving a legal dispute before a court delivers the final judgment.",
        "fun_explanation": "It's the 'let's not bother with the whole courtroom drama' solution - both sides compromise a bit so everyone can go home earlier!",
        "cartoon_description": "A cartoon showing two people shaking hands with pained expressions, each holding part of a dollar bill, with their lawyers looking disappointed about missing out on a trial."
    },
    "sidebar": {
        "simple_explanation": "A private conference between the judge and attorneys held outside of the jury's hearing.",
        "fun_explanation": "It's the legal version of 'can we talk in the hallway for a minute?' - a private huddle where lawyers and the judge discuss things they don't want the jury to hear!",
        "cartoon_description": "A cartoon showing a judge and lawyers huddled in a whispering circle, while the jury strains to hear what they're saying."
    },
    "slander": {
        "simple_explanation": "False spoken statements that harm a person's reputation.",
        "fun_explanation": "It's spreading rumors on the playground, but with legal consequences. 'Did you hear what they SAID about me?!' - but only if it's not true!",
        "cartoon_description": "A cartoon showing whispered words leaving one person's mouth and turning into daggers as they reach another person's reputation (shown as a balloon deflating)."
    },
    "sovereign immunity": {
        "simple_explanation": "A legal doctrine that prevents the government from being sued without its consent.",
        "fun_explanation": "It's the government's 'you can't touch me' card - like having permanent immunity in a game of tag unless they decide to let you catch them!",
        "cartoon_description": "A cartoon showing a government building surrounded by a force field that bounces off lawsuits, with a small door labeled 'We might let you sue us here.'"
    },
    "stare decisis": {
        "simple_explanation": "Latin for 'to stand by things decided.' The principle that courts should follow precedents set by prior decisions.",
        "fun_explanation": "It's the legal way of saying 'if it ain't broke, don't fix it' - judges should stick with what worked in similar cases before instead of reinventing the wheel!",
        "cartoon_description": "A cartoon showing a long line of judges each copying the ruling of the one before them, with an occasional rebel judge being pulled back in line."
    },
    "statute of limitations": {
        "simple_explanation": "A law that sets the maximum time after an event within which legal proceedings may be initiated.",
        "fun_explanation": "It's like a legal expiration date - after a certain amount of time, the court says 'sorry, this case is past its freshness date and can't be used anymore!'",
        "cartoon_description": "A cartoon showing a person rushing to the courthouse with a stopwatch ticking down as the statue of limitations is about to expire on their claim."
    },
    "subpoena": {
        "simple_explanation": "A written order requiring a person to appear in court to give testimony or to produce documents.",
        "fun_explanation": "It's the court's version of 'You HAVE to come to this party' - except it's not a party, and ignoring the invitation can get you in serious trouble!",
        "cartoon_description": "A cartoon showing a nervous-looking person receiving an official envelope with a judge's stamp on it, containing a gold-embossed mandatory invitation to court."
    },
    "summary judgment": {
        "simple_explanation": "A court decision made without a full trial when there is no genuine dispute about the material facts of the case.",
        "fun_explanation": "It's the legal fast-forward button - when a judge says 'This case is so obvious we don't need to waste time with a full trial!'",
        "cartoon_description": "A cartoon showing a judge pressing a 'SKIP TO END' button while lawyers are still setting up their presentations."
    },
    "testify": {
        "simple_explanation": "To give evidence as a witness in a court case, usually by speaking under oath.",
        "fun_explanation": "It's the 'please tell your version of what happened' part of court - where you promise to tell the truth and then everyone listens very carefully to exactly what you say!",
        "cartoon_description": "A cartoon showing a nervous witness in a stand with a spotlight on them, sweating as both lawyers stare intently at every word."
    },
    "torts": {
        "simple_explanation": "Civil wrongs that cause someone else to suffer loss or harm, resulting in legal liability for the person who commits the act.",
        "fun_explanation": "It's not about delicious cakes! It's about situations where someone does something wrong and owes you money for it - like legal 'oopsies' with consequences!",
        "cartoon_description": "A cartoon showing a person slipping on a banana peel with dollar signs floating up from the fall, while a lawyer stands nearby with a 'tort' calculator."
    },
    "venire": {
        "simple_explanation": "The group of people summoned to court from which a jury is selected.",
        "fun_explanation": "It's like the draft pool for the Jury All-Stars team - a bunch of regular citizens who might get picked to decide a case!",
        "cartoon_description": "A cartoon showing a diverse group of people in a waiting room holding jury summons, with some looking eager and others trying to find excuses to leave."
    },
    "venue": {
        "simple_explanation": "The geographical location where a case is heard, typically determined by where the crime occurred or the parties reside.",
        "fun_explanation": "It's picking the stage for your legal drama - should it play in New York or Los Angeles? The location matters for who makes the rules and who's in the audience!",
        "cartoon_description": "A cartoon showing lawyers arguing over a map with different courthouses, each trying to pull the case to their preferred location."
    },
    "verdict": {
        "simple_explanation": "The decision reached by a jury or judge in a legal case.",
        "fun_explanation": "It's the big reveal at the end of the legal show - the moment when everyone finds out who won and who lost after all the evidence and arguments!",
        "cartoon_description": "A cartoon showing a jury foreman dramatically opening an envelope marked 'VERDICT' with everyone in the courtroom on the edge of their seats."
    },
    "voir dire": {
        "simple_explanation": "The process where lawyers question potential jurors to determine if they are suitable for jury duty in a specific case.",
        "fun_explanation": "French for 'to speak the truth.' It's like a really awkward speed dating event where lawyers try to figure out if jurors will be fair or hold secret biases!",
        "cartoon_description": "A cartoon showing a lawyer with a clipboard interviewing nervous-looking people, with thought bubbles showing their hidden biases."
    },
    "waiver": {
        "simple_explanation": "The voluntary relinquishment or surrender of a known right or privilege.",
        "fun_explanation": "It's like telling the referee 'I know I could challenge that play, but I'm choosing not to' - you're giving up a right you would normally have!",
        "cartoon_description": "A cartoon showing a person signing away rights with a giant rubber stamp coming down on a document labeled 'YOUR RIGHTS' with 'WAIVED' appearing."
    },
    "warrant": {
        "simple_explanation": "A written order issued by a judicial officer authorizing police to make an arrest, search premises, or carry out some other action related to the administration of justice.",
        "fun_explanation": "It's the legal permission slip that police need before they can come into your house uninvited - the court's way of saying 'Yes, you can look for evidence there!'",
        "cartoon_description": "A cartoon showing police officers standing at a door with a giant golden ticket labeled 'SEARCH WARRANT' while a judge watches from a distance."
    },
    "writ": {
        "simple_explanation": "A formal written order issued by a court commanding the addressee to perform or refrain from performing a specified act.",
        "fun_explanation": "It's like a magical spell from the court - a powerful document that commands action and can't be ignored without serious consequences!",
        "cartoon_description": "A cartoon showing a court document with a royal seal and glowing edges being delivered by an official messenger, causing everyone who sees it to snap to attention."
    },
    "zealous advocacy": {
        "simple_explanation": "The ethical duty of lawyers to represent their clients with commitment and dedication, using all legal and ethical means to promote the client's interests.",
        "fun_explanation": "It's when your lawyer turns into your biggest fan and cheerleader, fighting for you like you're family - but still playing by the rules!",
        "cartoon_description": "A cartoon showing a lawyer in superhero pose with a cape labeled 'ZEALOUS ADVOCATE,' standing protectively in front of their client."
    },
    "hung jury": {
        "simple_explanation": "A jury that cannot agree on a verdict by the required voting margin after extended deliberations, resulting in a mistrial.",
        "fun_explanation": "It's like a family dinner where no one can agree on where to order takeout from, so everyone ends up going hungry and the decision gets postponed!",
        "cartoon_description": "A cartoon showing exhausted jurors divided down the middle of a table, pulling a rope in opposite directions with 'GUILTY' on one side and 'NOT GUILTY' on the other."
    },
    "probable cause": {
        "simple_explanation": "A reasonable basis for believing that a crime may have been committed or that evidence of a crime may be found in a particular place.",
        "fun_explanation": "It's when an officer has more than just a hunch but less than absolute certainty - like being 'pretty sure' your dog ate your homework because there are suspicious crumbs on his bed.",
        "cartoon_description": "A cartoon of a detective with a magnifying glass finding clues that form a question mark, not an exclamation point."
    }
}