(* Transcribing this projcect into OCaml to write it
 * more cleanly and uncover bugs in the original source. *)

open Core.Std

type description = string
type hours = Time.Span.t
type hours_done = Time.Span.t
type due = Date.t
let sub_span = Core.Span.(-)

type start_time = Time.t

type end_time = Time.t

(* one bool for every day of the week starting monday :) *)
type recurring = bool * bool * bool * bool * bool * bool * bool

(* use map: description -> task *)

type task =
  | Fixed of start_time * end_time * recurring
  | Homework_incomplete of hours * hours_done * due
  | Homework_complete of hours_done * due
  | NullTask

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

let tasks : (string * task * 'a) Map.t ref = ref String.Map.empty

let is_duplicate tsk =
  List.contains_dup (List.map (tsk::!tasks) ~f:get_description)

exception DuplicateTask

(* names are unique *)
let add_task desc tsk =
  if mem !tasks desc then raise DuplicateTask else
  tasks := !tasks.add desc tsks

(* todo: let it be removed by first few unique chars *)
let remove_task desc =
  tasks := String.Map.remove !tasks desc

let add_hours desc hrs =
  match String.Map.find !tasks desc with
  | None -> ()
  | Some x -> let add' v = tasks := String.Map.add !tasks desc v in
    (match x with
    | Fixed (s, e, r) -> () (* cannot add hours to fixed *)
    | Homework_incomplete (h, hd, d) ->
      let hd' = hd+hrs in if hd' >= h then () else add' (h, hd', d)
    | Homework_complete (hd, d) ->
      let hd' = hd+hrs in if hd' >= h then () else add' (h, hd', d)
    )

let get_due = function
  | Fixed _ -> None
  | Homework_incomplete (_, _, d) -> Some d
  | Homework_complete (_, d) -> Some d
  | NullTask -> None

let latest desc task_a (d_latest,t_latest) =
  match (get_due task_a, get_due t_latest) with
  | (None, None) -> (d_latest,t_latest)
  | (Some _, None) -> (desc,task_a)
  | (None, Some _) -> (d_latest,t_latest)
  | (Some a, Some b) -> if a < b then (d_latest,t_latest) else (desc,task_a)

let latest_task = String.Map.fold !tasks ~init:("no tasks", NullTask) ~f:latest

(* dropped: latest due date *)

(* next: addhours *)

(*
allocate hours available for each day until latest task in list

*)