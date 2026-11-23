"""Plain-language advice shown after a prediction.

IMPORTANT: this text is general guidance. Before the app is used by real
farmers, have it reviewed and edited by an agriculture expert (for example
your local Krishi Vigyan Kendra / agriculture officer). Keep the wording about
chemicals cautious: never state a dose, always say "check the label and ask an expert".
"""

SEEK_HELP = ("If many plants are affected, the spots are spreading quickly, or you are not sure, "
             "show the photos to your local agriculture officer or Krishi Vigyan Kendra (KVK) as soon as possible.")

TREATMENT_NOTE = ("These are options that are commonly discussed, not a prescription. Ask a local agriculture "
                  "officer for the right product, dose and timing, and always follow the label.")

INFO = {
    "Blast": {
        "summary": "A fungal disease that can attack the leaves, stems and the neck of the grain head. It spreads fast in humid, cloudy weather.",
        "signs": ["Spindle or diamond-shaped spots with grey or whitish centres and brown edges.",
                  "Spots can join together and dry out the whole leaf.",
                  "The neck below the grain head can turn brown or black and break."],
        "causes": ["The fungus Magnaporthe oryzae.",
                   "Long periods of wet leaves, high humidity and cool nights.",
                   "Too much nitrogen fertiliser, and varieties that are easily infected.",
                   "Infected seed or leftover straw and stubble."],
        "do_now": ["Walk the field and check how many plants show these spots.",
                   "Hold back extra nitrogen fertiliser for now.",
                   "Avoid water stress and keep the field water steady.",
                   "Take photos of several plants to show an agriculture officer."],
        "treatment": ["Fungicides such as tricyclazole are commonly used against blast; timing matters a lot.",
                      "Treating early, before the disease spreads to the grain heads, usually works better."],
        "prevention": ["Use blast-tolerant varieties recommended for your area.",
                       "Use clean, healthy seed and treat it before sowing.",
                       "Split nitrogen into smaller doses instead of one large dose.",
                       "Destroy infected straw and stubble after harvest."],
    },
    "Brown spot": {
        "summary": "A fungal disease that often appears where the soil is low in nutrients or the crop faces water stress.",
        "signs": ["Small, oval, brown spots, often with a yellow ring around them.",
                  "Older spots may get grey centres.",
                  "Dark spots can also appear on the grain husk."],
        "causes": ["The fungus Bipolaris oryzae.",
                   "Poor or nutrient-short soil and dry spells.",
                   "Infected seed, and warm, humid weather."],
        "do_now": ["Check whether the plants look short of nutrients or water.",
                   "Fix water stress if you can.",
                   "Take photos of several plants to show an agriculture officer."],
        "treatment": ["Fungicides such as mancozeb or propiconazole are sometimes used.",
                      "Improving soil nutrition often matters as much as spraying."],
        "prevention": ["Use clean, healthy seed and treat it before sowing.",
                       "Fertilise based on a soil test, including potassium.",
                       "Keep water supply steady through the season.",
                       "Clear weeds and destroy infected residue after harvest."],
    },
    "Bacterial leaf blight": {
        "summary": "A bacterial disease that spreads through water, wind-driven rain and infected seed. It can dry out leaves quickly.",
        "signs": ["Yellow or water-soaked stripes starting at the leaf tip or edges.",
                  "Stripes turn wavy, then white or straw-coloured, and the leaf dries.",
                  "In young plants the whole seedling can wilt."],
        "causes": ["The bacterium Xanthomonas oryzae pv. oryzae.",
                   "Flooding, storms and heavy rain that splash bacteria between plants.",
                   "Too much nitrogen fertiliser, and infected seed or stubble."],
        "do_now": ["Avoid walking through the wet field and then into healthy fields.",
                   "If you can, drain standing water.",
                   "Hold back extra nitrogen fertiliser for now.",
                   "Take photos of several plants to show an agriculture officer."],
        "treatment": ["There is no fully effective cure once it has spread, so prevention matters most.",
                      "Some copper-based products are sometimes advised; use them only on an expert's advice."],
        "prevention": ["Use resistant varieties recommended for your area.",
                       "Use clean seed and avoid damaging seedling tips at transplanting.",
                       "Split nitrogen into smaller doses.",
                       "Drain fields after heavy rain and destroy infected stubble."],
    },
    "Healthy": {
        "summary": "No disease pattern was found in this photo.",
        "signs": ["Leaf colour looks even, without spots or dry stripes."],
        "causes": [],
        "do_now": ["Keep checking leaves every week, especially after heavy rain or humid spells.",
                   "Check a few plants from different parts of the field, not just one."],
        "treatment": [],
        "prevention": ["Use clean seed and balanced fertiliser.",
                       "Keep water steady and clear weeds.",
                       "Check leaves every week during humid or rainy weather."],
    },
}
