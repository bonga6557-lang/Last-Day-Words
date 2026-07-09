-- Seed chapters and season_chapters (80 terms / 20 chapters)
insert into public.chapters (id, title, description, sort_order, season_id) values
  ('signs', 'Signs of Christ''s Return', 'Discover the warnings and symptoms of a world preparing for the Second Advent.', 0, null),
  ('shaking', 'The Shaking', 'Examine the great sifting process within the church as truth and error collide.', 1, null),
  ('latter-rain', 'The Latter Rain', 'The magnificent outpouring of the Holy Spirit to prepare the harvest for the end.', 2, null),
  ('loud-cry', 'The Loud Cry', 'The final warning warning to the world, swelling into a global shout.', 3, null),
  ('seal-of-god', 'The Seal of God', 'The ultimate sign of allegiance in the final test of worship.', 4, null),
  ('time-of-trouble', 'The Time of Trouble', 'The final severe crisis and trial of faith for God''s faithful remnant.', 5, null),
  ('second-coming', 'The Second Coming', 'The glorious, triumphant return of Jesus Christ in majesty and power.', 6, null),
  ('new-earth', 'Heaven and the New Earth', 'The restoration of all things and the eternal reign of peace and joy.', 7, null),
  ('judgment', 'The Investigative Judgment', 'Understand the pre-Advent heavenly court and the cleansing of the sanctuary before Christ returns.', 8, null),
  ('deceptions', 'Last-Day Deceptions', 'Recognize Satan''s final delusions — spiritualism, strong delusion, and the gathering at Armageddon.', 9, null),
  ('daniel-image', 'Daniel: The Great Image', 'Nebuchadnezzar''s dream of the multi-metal statue and the stone cut without hands.', 10, 'daniel'),
  ('daniel-beasts', 'Daniel: Four Beasts', 'The night vision of four great beasts rising from the sea — successive world powers.', 11, 'daniel'),
  ('daniel-horn', 'Daniel: The Little Horn', 'The blasphemous power that rises among the ten horns and speaks great words against the Most High.', 12, 'daniel'),
  ('daniel-sanctuary', 'Daniel: Sanctuary Cleansed', 'The 2300-day prophecy and the cleansing of the sanctuary in heaven.', 13, 'daniel'),
  ('daniel-stand', 'Daniel: Michael Stands Up', 'The close of the book of Daniel — Michael, the sealed book, and the wise who shine.', 14, 'daniel'),
  ('rev-churches', 'Revelation: Seven Churches', 'Christ''s letters to the seven churches of Asia — counsel for every age of the church.', 15, 'revelation'),
  ('rev-seals', 'Revelation: Seven Seals', 'The Lamb opens the sealed book — conquest, conflict, scarcity, and the cry of the martyrs.', 16, 'revelation'),
  ('rev-trumpets', 'Revelation: Seven Trumpets', 'Trumpet judgments that warn the earth as history moves toward the final crisis.', 17, 'revelation'),
  ('rev-beast', 'Revelation: The Beast System', 'Sea beast, earth beast, and the image that enforces false worship in the final crisis.', 18, 'revelation'),
  ('rev-millennium', 'Revelation: The Millennium', 'The thousand years, the binding of Satan, and the final judgment after the first resurrection.', 19, 'revelation')
on conflict (id) do update set title = excluded.title, description = excluded.description, sort_order = excluded.sort_order, season_id = excluded.season_id;

insert into public.season_chapters (season_id, chapter_id) values
  ('daniel', 'daniel-image'),
  ('daniel', 'daniel-beasts'),
  ('daniel', 'daniel-horn'),
  ('daniel', 'daniel-sanctuary'),
  ('daniel', 'daniel-stand'),
  ('revelation', 'rev-churches'),
  ('revelation', 'rev-seals'),
  ('revelation', 'rev-trumpets'),
  ('revelation', 'rev-beast'),
  ('revelation', 'rev-millennium')
on conflict do nothing;
