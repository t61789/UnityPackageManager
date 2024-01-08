import processTask

cur_work_path = "D:\\GitLocal"
_ , cur_branch_name, _ = processTask.execute_cmd_simple(["git", "rev-parse", "--abbrev-ref", "HEAD"], cur_work_path)
print("done")
_ , cur_upstream_name, _ = processTask.execute_cmd_simple(["git", "rev-parse", "--abbrev-ref", "HEAD@{upstream}"], cur_work_path)
print("done")

if cur_branch_name.endswith("\n"):
    cur_branch_name = cur_branch_name[:-1]
if cur_upstream_name.endswith("\n"):
    cur_upstream_name = cur_upstream_name[:-1]

processTask.execute_cmd(
    lambda line: print(line),
    lambda line: print(line),
    None,
    ["git", "checkout", "-B", cur_branch_name, cur_upstream_name, "--progress", "-f"],
    cur_work_path
)

