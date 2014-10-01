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

type task =
  | Fixed of description * start_time * end_time * recurring
  | Homework_incomplete of description * hours * hours_done * due
  | Homework_complete of description * hours_done * due

let recurring_to_string (m,t,w,u,f,s,n) =
  let day_list = [m;t;w;u;f;s;n] in
  let day_names = ["Monday"; "Tuesday"; "Wednesday"; "Thursday"; "Friday"; "Saturday"; "Sunday"] in
  let zipped = List.zip_exn day_list day_names in
  let filtered = List.filter zipped (fun (b,_) -> b) in
  let mapped = List.map filtered (fun (_,d) -> d) in
  String.concat ~sep:" " mapped

let task_to_string = function
  | Fixed (desc, start_t, end_t, recr) ->
      let rec_s = recurring_to_string recr in
      desc ^ ", Start time: " ^ Time.to_string start_t ^ ", End time: " ^ Time.to_string end_t ^ ", Recurring days: " ^ rec_s
  | Homework_incomplete (desc, hrs, hrsdn, due) ->
      desc ^ ", Time left: " ^ Time.Span.to_short_string (sub_span hrs hrsdn) ^ ", Days left: " ^ string_of_int (Date.diff due (Date.today()))
  | Homework_complete (desc, hrsdn, due) ->
      desc ^ " (The due date for this task, " ^ Date.to_string due ^ ", has elapsed."

let tasks : task list ref = ref []

let get_description = function
  | Fixed (d,_,_,_) -> d
  | Homework_incomplete (d,_,_,_) -> d
  | Homework_complete (d,_,_) -> d

let is_duplicate tsk =
  List.contains_dup (List.map (tsk::!tasks) get_description)

exception DuplicateTask

(* names are unique *)
let add_task tsk =
  if is_duplicate tsk then raise DuplicateTask else
  tasks := tsk::!tasks

(* todo: let it be removed by first few unique chars *)
let remove_task desc =
  tasks := List.filter !tasks (fun s -> get_description s <> desc)

(* dropped: latest due date *)

(* next: addhours *)