create or replace function public.validate_speed_score()
returns trigger
language plpgsql
as $$
begin
  if NEW.score < 0 or NEW.words_solved < 0 then
    raise exception 'score and words_solved must be non-negative';
  end if;
  if NEW.words_solved > 80 then
    raise exception 'words_solved exceeds maximum (80)';
  end if;
  if NEW.score > NEW.words_solved * 400 then
    raise exception 'score exceeds maximum for words_solved';
  end if;
  return NEW;
end;
$$;

drop trigger if exists speed_scores_validate on public.speed_scores;
create trigger speed_scores_validate
  before insert or update on public.speed_scores
  for each row execute function public.validate_speed_score();
