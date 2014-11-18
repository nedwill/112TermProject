(* Transcribing this project into OCaml to write it
 * more cleanly and uncover bugs in the original source. *)

open Core.Std

type description = string
type hours = Time.Span.t
type hours_done = Time.Span.t
type due = Date.t
type start_time = Time.t
type end_time = Time.t

type recurring = bool * bool * bool * bool * bool * bool * bool
type task =
  | Fixed of start_time * end_time * recurring
  | Homework_incomplete of hours * hours_done * due
  | Homework_complete of hours_done * due
  | NullTask

let sub_span = Core.Span.(-)
let add_span = Core.Span.(+)

let recurring_to_string (m,t,w,u,f,s,n) =
  let day_list = [m;t;w;u;f;s;n] in
  let day_names = ["Monday"; "Tuesday"; "Wednesday"; "Thursday";
    "Friday"; "Saturday"; "Sunday"] in
  let zipped = List.zip_exn day_list day_names in
  let filtered = List.filter zipped ~f:(fun (b,_) -> b) in
  let mapped = List.map filtered ~f:(fun (_,d) -> d) in
  String.concat ~sep:" " mapped

let task_to_string = function
  | Fixed (start_t, end_t, recr) ->
      let rec_s = recurring_to_string recr in
      ", Start time: " ^ Time.to_string start_t ^ ", End time: "
        ^ Time.to_string end_t ^ ", Recurring days: " ^ rec_s
  | Homework_incomplete (hrs, hrsdn, due) ->
      ", Time left: " ^ Time.Span.to_short_string (sub_span hrs hrsdn)
        ^ ", Days left: " ^ string_of_int (Date.diff due (Date.today()))
  | Homework_complete (_, due) ->
      " (The due date for this task, " ^ Date.to_string due
        ^ ", has elapsed."
  | NullTask -> "Null task. You shouldn't see this."

let tasks = ref String.Map.empty

exception DuplicateTask

(* names are unique *)
let add_task desc tsk =
  if Map.mem !tasks desc then raise DuplicateTask else
  tasks := Map.add !tasks ~key:desc ~data:tsk

(* todo: let it be removed by first few unique chars *)
let remove_task desc =
  tasks := Map.remove !tasks desc

let add_hours desc hrs =
  match Map.find !tasks desc with
  | None -> ()
  | Some x -> let add' v = tasks := Map.add !tasks ~key:desc ~data:v in
    (match x with
    | Fixed _ | NullTask -> () (* cannot add hours to fixed/nulltask *)
    | Homework_incomplete (h, hd, d) ->
      let hd' = add_span hd hrs in
      if hd' >= h then
        add' (Homework_complete (hd', d)) (* becomes complete *)
      else
        add' (Homework_incomplete (h, hd', d))
    | Homework_complete (hd, d) ->
      let hd' = add_span hd hrs in
      add' (Homework_complete (hd', d))
    )

let get_due = function
  | Fixed _ -> None
  | Homework_incomplete (_, _, d) -> Some d
  | Homework_complete (_, d) -> Some d
  | NullTask -> None

let latest ~key:desc ~data:task_a (d_latest,t_latest) =
  match (get_due task_a, get_due t_latest) with
  | (None, None) -> (d_latest,t_latest)
  | (Some _, None) -> (desc,task_a)
  | (None, Some _) -> (d_latest,t_latest)
  | (Some a, Some b) -> if a < b then (d_latest,t_latest) else (desc,task_a)

let get_latest_task : unit -> (string * task) =
  (fun () -> Map.fold !tasks ~init:("no tasks", NullTask) ~f:latest)

exception AddHoursToFixed

let add_hours_to_task hours = function
  | Fixed _ -> raise AddHoursToFixed
  | Homework_incomplete (hours_i, hours_done, due) ->
    Homework_incomplete (hours_i+hours, hours_done, due)
  | Homework_complete (hours_done, due) -> Homework_complete (hours_done, due)
  | NullTask -> NullTask

let add_hours_by_desc description hours =
  let old_task = String.Map.find !tasks description in
  let new_task = add_hours_to_task hours old_task in
  tasks != String.Map.add !tasks description new_task

(*
  next: calcAgenda
*)

(* dropped: latest due date *)

(*
allocate hours available for each day until latest task in list
*)