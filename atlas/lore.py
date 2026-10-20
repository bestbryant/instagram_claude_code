"""Lore for planets requested by name in the comments.

Each concept pairs a short entry with the visual features it needs, so the
picture matches the text. Everything is seeded by the name: the same name
always charts the same planet.
"""
from __future__ import annotations

import unicodedata
from dataclasses import asdict

from .render import Seeds, Spec, random_spec, seed_from

CONCEPTS = [
    dict(subtitle="the upward snow",
         story="Snow on {name} falls up. It comes off the hills slowly in the early morning, and by midday the valleys are bare and the clouds are very full. It settles again in the evening, mostly in the same places. Children leave footprints in it before it goes, to see whether they come back.",
         hook="Snow on {name} falls up.", reel=["It lifts off the hills in the morning.", "It comes back down in the evening, mostly where it was."],
         spec=dict(snow=True, particles="snow_up", palette=["violet_ice", "polar_night", "pastel"])),
    dict(subtitle="the one cloud",
         story="There is one cloud on {name}. It's very large and very slow, and the people who live there call it Margaret. When Margaret passes over a town, work stops and everyone goes outside to stand in the shade. She takes about a year to get all the way round.",
         hook="There is exactly one cloud on {name}, and it has a name.", reel=["It's very large and very slow.", "When it passes over, everyone goes outside."],
         spec=dict(gag="big_cloud", mist=0.4, crowd=3, crowd_items="nothing", crowd_facing="")),
    dict(subtitle="the uphill rivers",
         story="Every river on {name} runs uphill and ends in the same lake, high in the mountains. The lake has been filling for as long as anyone has measured it. Nobody knows what happens when it's full. The engineers say not to worry about it, which nobody finds reassuring.",
         hook="Every river on {name} runs uphill.", reel=["They all end in the same lake.", "Nobody knows what happens when it's full."],
         spec=dict(water=True, shore=["left", "right"])),
    dict(subtitle="the kind echoes",
         story="Echoes on {name} come back softened. Shout something unkind into a canyon and what returns is closer to an apology. People make long trips out to the cliffs to say things they regret, and stand there listening to them come back gentler.",
         hook="Echoes on {name} come back kinder than you sent them.", reel=["Shout something unkind into the canyon.", "What comes back is closer to an apology."],
         spec=dict(terrain="mesas", crowd=1, crowd_items="shout", crowd_x=0.3, crowd_facing="right")),
    dict(subtitle="the Sunday wind",
         story="The wind on {name} only blows on Sundays. The rest of the week is spent building kites in sheds and kitchens. By Sunday morning there are more kites than people, and the sky over the hills stays crowded until dark.",
         hook="The wind on {name} only blows on Sundays.", reel=["All week, people build kites.", "On Sunday the sky is crowded until dark."],
         spec=dict(terrain="hills", crowd=3, crowd_items="kite", sun_x=0.3)),
    dict(subtitle="the audible stars",
         story="The stars over {name} make a sound, a faint crackle like a fire in another room. You only hear it on clear nights, away from town. People with insomnia move there and sleep properly for the first time in years. People who like silence move away.",
         hook="On clear nights, you can hear the stars over {name}.", reel=["A faint crackle, like a fire in another room.", "Insomniacs move there to sleep."],
         spec=dict(stars=1.4, suns=0, palette=["teal_night", "polar_night", "violet_ice", "abyss"])),
    dict(subtitle="the slow moons",
         story="The two moons of {name} circle each other slowly, and a full turn takes about forty years. Couples tend to marry when the moons line up, and the custom is that you stay together at least until they line up again. Most do. A few renegotiate.",
         hook="The moons of {name} take forty years to circle each other.", reel=["Couples marry when they line up.", "You stay together until they line up again."],
         spec=dict(gag="two_moons", moons=0, suns=0, giant=False, big_moon=False)),
    dict(subtitle="the glowing night",
         story="One night a year, the sea around {name} glows from underneath, a cold blue-green that lights up the bottoms of the boats. Nobody fishes that night. Most of the coast sits on the sand until it fades, at around four in the morning.",
         hook="One night a year, the sea on {name} glows.", reel=["Nobody fishes that night.", "The whole coast sits on the sand until it fades."],
         spec=dict(water=True, shore=["left", "right"], sea_glow=True, suns=0, stage=0.8,
                   palette=["abyss", "teal_night", "polar_night"])),
    dict(subtitle="the slow valleys",
         story="Time passes more slowly in the valleys of {name} and faster on the peaks. Patient people live at the bottom. Impatient people live at the top, where they age quickly and get a lot done. Families tend to meet halfway.",
         hook="Time runs slower in the valleys of {name}.", reel=["Patient people live at the bottom.", "Families tend to meet halfway."],
         spec=dict(terrain="peaks", mist=1.0)),
    dict(subtitle="the lost property coast",
         story="Things lost elsewhere wash up on the beaches of {name}: odd socks, house keys, umbrellas, a surprising number of wedding rings. There's a lost property office the size of a small city. If you can describe something well enough, they'll post it back.",
         hook="Everything you've lost ends up on {name}.", reel=["Umbrellas, kettles, odd socks, wedding rings.", "Describe it well enough and they'll post it back."],
         spec=dict(water=True, shore=["left", "right"], crowd=3, crowd_items="umbrella,kettle,book")),
    dict(subtitle="the slow sunrise",
         story="Light moves slowly on {name}, so sunrise takes most of the morning to reach you. You can watch it come across the hills like a tide. If you're not ready for it, you can walk the other way for a while.",
         hook="Sunrise on {name} takes all morning.", reel=["You can watch it come across the hills.", "If you're not ready, walk the other way."],
         spec=dict(suns=1, sun_y=0.5, sun_x=0.5, sun_size=0.08, terrain="hills", trees="none", big_moon=False, giant=False,
                   palette=["gold_hour", "rose_fog", "mint_dawn"])),
    dict(subtitle="the singing range",
         story="The spires on {name} sing when the wind gets up: low notes from the big ones, high notes from the small. A few have been carved slightly to tune them. On the right afternoon the whole range plays something that very nearly sounds like a song.",
         hook="The mountains on {name} sing when it's windy.", reel=["Low notes from the big ones, high notes from the small.", "A few have been carved to tune them."],
         spec=dict(terrain="spires", crowd=2, crowd_items="kite,nothing")),
    dict(subtitle="the lingering shadows",
         story="Shadows on {name} stay where they fall for about an hour after you've gone, so you can see where your friends have been all afternoon. People in love leave theirs on each other's doorsteps. This is considered sweet, and occasionally a bit much.",
         hook="Your shadow stays behind on {name}.", reel=["It lingers for about an hour.", "People in love leave theirs on doorsteps."],
         spec=dict(snow=True, palette=["pastel", "violet_ice"], suns=1, sun_x=0.12, sun_y=0.5, house=False, trees="none",
                   giant=False, big_moon=False, islands=0, crowd=2, crowd_items="shadowed,shadow",
                   cartographer=False)),     # nobody else on the snow: the shadow has to read as nobody's
    dict(subtitle="the long jumps",
         story="Gravity on {name} is light enough that a decent jump lasts about a minute. A lot of conversations happen in the air. It's considered rude to land before the other person has finished their sentence.",
         hook="One jump on {name} lasts about a minute.", reel=["Conversations happen mid-air.", "It's rude to land before someone has finished talking."],
         spec=dict(islands=0, crowd=2, crowd_items="nothing,aloft", crowd_facing="in", crowd_x=0.5)),
    dict(subtitle="the humming ridges",
         story="The crystal ridges on {name} hold on to sound. Anything sung near them comes back, very quietly, for years afterwards. Walk through the valley at dusk and you can hear a century of people humming under their breath.",
         hook="The crystals on {name} remember every song.", reel=["Anything sung near them comes back for years.", "At dusk the whole valley hums."],
         spec=dict(terrain="crystal", glow_rims=True)),
    dict(subtitle="the long evening",
         story="Sunset on {name} lasts about eleven hours. People plan their days around the light: errands in the gold part, dinner in the pink, long walks once it turns purple. I have never met anyone there who was in a hurry to get home.",
         hook="Sunset on {name} lasts eleven hours.", reel=["Errands in the gold part, dinner in the pink.", "Long walks once it turns purple."],
         spec=dict(suns=1, sun_y=0.52, palette=["gold_hour", "lilac_dusk", "rose_fog", "crimson"])),
    dict(subtitle="the ring shadow",
         story="The rings of the giant over {name} throw a long stripe of shade across one hemisphere. All the towns are inside it, where midday is cool and dim. Moving out into the full sun is something people do when they're young and want to make a point.",
         hook="Everyone on {name} lives in the shadow of a ring.", reel=["Midday there is cool and dim.", "Moving into the sun is a teenage rebellion."],
         spec=dict(giant=True, ring=True, big_moon=False)),
    dict(subtitle="the lighthouse letters",
         story="Every cove on {name} has a lighthouse, and each keeper writes a letter to the next one along the coast. The letters have been going around the planet for three hundred years. I was allowed to read one. It was mostly about the weather, and a dog.",
         hook="The lighthouse keepers on {name} write to each other.", reel=["Each keeper writes to the next along the coast.", "The letters have gone round for three hundred years."],
         spec=dict(water=True, shore=["left", "right"], lighthouse=True)),
    dict(subtitle="the shared dream",
         story="On {name}, everyone has the same dream on the same night. Breakfast is mostly spent comparing details. Last week, I'm told, it was about a very polite whale who wanted directions to the station.",
         hook="Everyone on {name} has the same dream.", reel=["Breakfast is mostly comparing details.", "Last week: a polite whale asking for directions."],
         spec=dict(suns=0, house=True, palette=["teal_night", "polar_night", "abyss"], stars=1.2)),
    dict(subtitle="the honest flowers",
         story="Flowers on {name} only open when someone nearby says something true. The gardens around the courthouse are badly overgrown. First dates tend to be quiet, and very floral.",
         hook="Flowers on {name} only open for the truth.", reel=["The courthouse gardens are overgrown.", "First dates are quiet, and very floral."],
         spec=dict(palette=["rose_fog", "pastel", "lilac_dusk"], trees="lone", daisies=45, stage=0.7)),
    dict(subtitle="the lit moon",
         story="The moon over {name} is hollow, and every evening a light comes on inside it. Nobody has gone up to see who it is. The general feeling is that it would be rude.",
         hook="Every evening, a light comes on inside the moon of {name}.", reel=["Nobody has gone up to see who it is.", "It would feel rude."],
         spec=dict(big_moon=True, giant=False, suns=0, moon_window=True)),
    dict(subtitle="the walking forests",
         story="The forests on {name} move, very slowly, towards wherever the light is best. A forest can cross a valley in about a hundred years. The maps are always out of date, and the foresters are always slightly out of breath.",
         hook="The forests on {name} walk.", reel=["A forest can cross a valley in a century.", "The maps are always out of date."],
         spec=dict(trees="pines")),
    dict(subtitle="the voted weather",
         story="Weather on {name} is decided by a vote at seven every morning. Rain wins most days. Officially that's for the crops. Unofficially, people just like the sound of it on the roof.",
         hook="On {name}, the weather is decided by vote.", reel=["Rain wins most days.", "People just like the sound of it on the roof."],
         spec=dict(particles="rain", house=True, crowd=4, crowd_items="umbrella")),
    dict(subtitle="the one snowflake",
         story="Every snowflake on {name} is exactly the same shape. The people who live there find this restful. Their poets have been writing about the one shape for six hundred years and say they're nowhere near done.",
         hook="Every snowflake on {name} is the same shape.", reel=["People there find it restful.", "The poets aren't done with it yet."],
         spec=dict(snow=True, particles="snow", gag="same_flakes", palette=["violet_ice", "polar_night"])),
]


# The short cut of each concept (docs/PLAN.md): the premise as the big line, the requester under it, and an onset at
# 0.4 s that enacts the premise. "before" is the scene for the first 0.4 s; after it, the planet as charted. Each
# beat is (framing, scene changes) for one of the concept's two reel lines; "end" closes the end card.
REQUEST_VERSION = "A"   # silent: the voice can't be trusted with every requester's name
SHORTS = {
    "the upward snow": dict(title="Snow on {name} falls up.", before=dict(particles="none"), framing="medium",
                            beats=[("wide", None), ("medium", dict(particles="snow", palette="lilac_dusk"))],
                            end="Footprints usually come back."),
    "the one cloud": dict(title="There is exactly one cloud on {name}.", before=dict(gag=""), framing="gag",
                          beats=[("wide", None), ({"framing": "medium", "focus": [0.5, 0.52]}, None)], end="Her name is Margaret."),
    "the uphill rivers": dict(title="Every river on {name} runs uphill.", before=dict(water=False), framing="wide",
                              beats=[("wide", None), ("medium", None)], end="The engineers say not to worry."),
    "the kind echoes": dict(title="Echoes on {name} come back kinder.", before=dict(crowd_items="nothing"), framing="crowd",
                            beats=[("crowd", None), ("medium", dict(crowd_items="echo"))], end="People go there to say sorry."),
    "the Sunday wind": dict(title="The wind on {name} only blows on Sundays.", before=dict(crowd_items="nothing"),
                            framing="medium", beats=[("crowd", dict(crowd_items="nothing")), ("wide", dict(crowd=5))],
                            end="Monday is very quiet."),
    "the audible stars": dict(title="You can hear the stars over {name}.", before=dict(stars=0.0, palette="lilac_dusk", suns=1, sun_y=0.6),
                              framing="sky",
                              beats=[("sky", None), ("wide", dict(house=True))], end="People who like silence move away."),
    "the slow moons": dict(title="The moons of {name} take forty years to line up.", before=dict(gag=""), framing="gag",
                           zoom=(1.3, 1.36),
                           beats=[("wide", dict(gag="two_moons_aligned", crowd=2, crowd_items="nothing", crowd_facing="in", crowd_x=0.5)),
                                  ("wide", dict(crowd=2, crowd_items="nothing", crowd_facing="in", crowd_x=0.5))],
                           end="A few renegotiate."),
    "the glowing night": dict(title="One night a year, the sea on {name} glows.", before=dict(sea_glow=False),
                              framing="wide", beats=[("medium", None), ("wide", dict(crowd=4, crowd_items="nothing"))],
                              end="It fades at about four in the morning."),
    "the slow valleys": dict(title="Time runs slower in the valleys of {name}.", before=dict(mist=0.0), framing="medium",
                             beats=[("wide", None), ("medium", dict(crowd=2, crowd_items="nothing", crowd_facing="in"))],
                             end="Birthdays are complicated."),
    "the lost property coast": dict(title="Everything you've lost ends up on {name}.", before=dict(crowd=0), framing="crowd",
                                    beats=[("crowd", None), ("wide", dict(house=True))], end="Mostly socks."),
    "the slow sunrise": dict(title="Sunrise on {name} takes all morning.", before=dict(sun_y=0.8, palette="teal_night"),
                             framing="wide", beats=[("wide", None), ("medium", dict(crowd=1, crowd_items="nothing"))],
                             end="Breakfast runs late."),
    "the singing range": dict(title="The mountains on {name} sing when it's windy.", before=dict(crowd_items="nothing"),
                              framing="crowd", beats=[("wide", None), ({"framing": "medium", "focus": [0.5, 0.42]}, None)],
                              end="On a good day, it's nearly a song."),
    "the lingering shadows": dict(title="Your shadow stays behind on {name}.", before=dict(crowd_items="shadowed,shadowed"),
                                  motion="cut", framing="wide", zoom=(1.6, 1.68), focus=(0.8, 0.68),
                                  beats=[("wide", None),
                                         ("house", dict(house=True, house_x=0.84, crowd=1, crowd_items="shadow", crowd_x=0.7))],
                                  end="Sweet. Occasionally a bit much."),
    "the long jumps": dict(title="One jump on {name} lasts about a minute.", before=dict(crowd_items="nothing,nothing"),
                           motion="cut", framing="wide",
                           beats=[("wide", None), ({"framing": "medium", "focus": [0.5, 0.55]}, None)], end="Nobody interrupts."),
    "the humming ridges": dict(title="The crystals on {name} remember every song.", before=dict(glow_rims=False),
                               framing="medium", beats=[("medium", None), ("wide", dict(palette="lilac_dusk"))],
                               end="Mind what you hum."),
    "the long evening": dict(title="Sunset on {name} lasts eleven hours.", before=dict(palette="cobalt_noon", sun_y=0.3),
                             framing="wide", beats=[("wide", dict(palette="gold_hour")),
                                                    ("medium", dict(palette="lilac_dusk", crowd=2, crowd_items="nothing"))],
                             end="Nobody hurries home."),
    "the ring shadow": dict(title="Everyone on {name} lives in the shadow of a ring.", before=dict(ring=False),
                            motion="cut", framing="giant", beats=[("wide", None), ("medium", dict(crowd=1, crowd_items="nothing"))],
                            end="Most move back by thirty."),
    "the lighthouse letters": dict(title="The lighthouse keepers on {name} write to each other.", before=dict(lighthouse=False),
                                   framing="lighthouse", beats=[("wide", None), ("lighthouse", None)],
                                   end="Mostly about the weather, and a dog."),
    "the shared dream": dict(title="Everyone on {name} has the same dream.", before=dict(palette="gold_hour", suns=1, stars=0.0),
                             framing="wide", beats=[("crowd", dict(palette="mint_dawn", suns=1, stars=0.0, crowd=3, crowd_items="cup")),
                                                    ("wide", None)],
                             end="Nobody knew the way to the station."),
    "the honest flowers": dict(title="Flowers on {name} only open for the truth.", before=dict(daisies=0), framing="wide",
                               zoom=(1.3, 1.36), focus=(0.5, 0.6),
                               beats=[("medium", dict(daisies=90)),
                                      ("crowd", dict(crowd=2, crowd_items="nothing", crowd_facing="in", crowd_x=0.5))],
                               end="Compliments are taken seriously."),
    "the lit moon": dict(title="A light comes on inside the moon of {name}.", before=dict(moon_window=False), framing="moon",
                         beats=[("wide", dict(crowd=2, crowd_items="nothing")), ("moon", None)], end="Somebody's home."),
    "the walking forests": dict(title="The forests on {name} walk.", before=dict(trees="none"), framing="medium",
                                beats=[("wide", None), ("medium", dict(trees="none"))],
                                end="The foresters are always out of breath."),
    "the voted weather": dict(title="On {name}, the weather is decided by vote.", before=dict(particles="none", crowd_items="nothing"),
                              motion="cut", framing="crowd", beats=[("crowd", None), ("house", None)],
                              end="Sunshine has a small, loyal following."),
    "the one snowflake": dict(title="Every snowflake on {name} is the same shape.", before=dict(particles="none", gag=""), framing="gag",
                              beats=[("wide", dict(crowd=1, crowd_items="nothing")), ("medium", None)],
                              end="Six hundred years so far."),
}

RULES = ["Visitors must sign the guest book. The guest book signs back.",
         "No whistling after dark. Something always whistles back.",
         "Every new arrival is assigned a cat, whether they like it or not.",
         "Maps may be borrowed but must be returned slightly improved.",
         "Hats must be held on to at all times. The wind is a collector.",
         "Complaints about the weather go to the weather, in writing.",
         "It is illegal to be in a hurry before noon.",
         "Anyone who names a star has to look after it.",
         "Do not feed the clouds.",
         "The last person awake turns off the moon."]
QUESTIONS = ["Would you visit?", "Would you stay a week, or for good?", "Who would you take with you?",
             "Would you get used to it?", "What would you pack?"]

TAGS = ["#worldbuilding", "#illustration"]
EXTRA_TAGS = ["#imaginaryworlds", "#scifiart", "#fantasyart", "#shortstory", "#spaceart"]


def _pick(rng, x):
    return x[int(rng.integers(0, len(x)))] if isinstance(x, list) else x


def _population(rng):
    n = int(10 ** rng.uniform(1.6, 6.5))
    if n < 1000:
        return str(n)
    if n < 1_000_000:
        return f"about {round(n, -3):,}"
    return f"{n / 1e6:.1f} million"


def short_cut(concept: dict, spec: Spec, display: str, by: str | None = None) -> dict:
    """The request's short Reel (atlas/reel.py short_shots) from its concept's template."""
    t = SHORTS[concept["subtitle"]]
    onset = {"at": 0.4, "spec": {k: getattr(spec, k) for k in t["before"]}}
    if t.get("motion"):
        onset["motion"] = t["motion"]
    beats = []
    for line, (shot, change) in zip(concept["reel"], t["beats"]):
        beats.append({"text": line, "shot": shot, **({"spec": dict(change)} if change else {})})
    camera = {k: list(t[k]) for k in ("zoom", "focus") if k in t}
    return {"version": REQUEST_VERSION, "title": t["title"].format(name=display),
            "sub": f"{by} asked for this one." if by else "Every name has a planet.",
            "framing": t["framing"], **camera, "spec": dict(t["before"]), "onset": onset, "beats": beats, "end": t["end"]}


def chart(name: str, number: str | None = None, by: str | None = None) -> tuple[dict, Spec, int]:
    """Return (entry, spec, seed) for any name."""
    clean = "".join(c for c in name if unicodedata.category(c)[0] in "LNPZM")
    name = " ".join((clean or name).split()).strip()
    display = name if any(c.isupper() for c in name) else name.title()
    seed = seed_from(name)
    rng = Seeds(seed).rng("lore")
    concept = CONCEPTS[int(rng.integers(0, len(CONCEPTS)))]

    spec = random_spec(seed)
    spec.particles = "none"
    for k, v in concept["spec"].items():
        setattr(spec, k, _pick(rng, v))
    if spec.water and spec.shore == "none" and (spec.lighthouse or spec.figure):
        spec.shore = _pick(rng, ["left", "right"])
    if spec.water:
        spec.glass_waves = False
        spec.layers = min(spec.layers, 4)
    if spec.big_moon:
        spec.giant = False
    if spec.lighthouse:
        spec.house = False         # a house would raise the ledge in front of the lighthouse
    if spec.particles in ("snow", "snow_up"):
        spec.snow = True
    later = [c for _, c in SHORTS[concept["subtitle"]]["beats"] if c]
    if any(x.get("crowd") or x.get("daisies") or x.get("house") for x in [asdict(spec)] + later) and not spec.stage:
        spec.stage = 0.72          # a ledge lifts the people, flowers and houses clear of Instagram's caption area

    moons = "1, very close" if spec.big_moon else "none" if spec.moons == 0 else str(spec.moons)
    facts = {
        "Day": f"{int(rng.integers(5, 49))} hours",
        "Moons": moons,
        "Gravity": f"{rng.uniform(0.2, 1.7):.1f} g",
        "Population": _population(rng),
    }
    entry = {
        "id": number or f"R{seed % 1000:03d}",
        "name": display,
        "subtitle": concept["subtitle"],
        "story": concept["story"].format(name=display),
        "facts": facts,
        "hook": concept["hook"].format(name=display),
        "beats": concept["reel"],
        "reel_lines": concept["reel"],
        "odd_line": concept["reel"][1],
        "rule": _pick(rng, RULES),
        "question": _pick(rng, QUESTIONS),
        "tags": TAGS + [_pick(rng, EXTRA_TAGS)],
        "spec": asdict(spec),
        "short": short_cut(concept, spec, display, by),
    }
    return entry, spec, seed
