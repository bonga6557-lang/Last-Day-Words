import type { Season } from "../types";

/** Bundled seasonal tracks (Daniel + Revelation). */
export const BUNDLED_SEASONS: Season[] = [
  {
    id: "daniel",
    title: "Daniel Track",
    description:
      "Prophetic milestones from the book of Daniel — image, beasts, little horn, sanctuary, and Michael.",
    startsOn: null,
    endsOn: null,
    chapterIds: [
      "daniel-image",
      "daniel-beasts",
      "daniel-horn",
      "daniel-sanctuary",
      "daniel-stand",
      "daniel-three",
      "daniel-five",
      "daniel-six",
      "daniel-nine",
      "daniel-ten",
      "daniel-one",
    ],
  },
  {
    id: "revelation",
    title: "Revelation Track",
    description:
      "Prophetic milestones from Revelation — churches, seals, trumpets, beast system, and the millennium.",
    startsOn: null,
    endsOn: null,
    chapterIds: [
      "rev-churches",
      "rev-seals",
      "rev-trumpets",
      "rev-beast",
      "rev-millennium",
      "rev-throne",
      "rev-144000",
      "rev-witnesses",
      "rev-woman-dragon",
      "rev-harvest",
      "rev-plagues",
      "rev-harlot",
      "rev-victory",
      "rev-new-creation",
      "rev-letters",
      "rev-final",
    ],
  },
];
