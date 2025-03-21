"""
Output autoupdate PR text

Also update changelog
"""

import argparse
from datetime import date


parser = argparse.ArgumentParser()
parser.add_argument("--repo", help="Tool repo")
parser.add_argument("--log", help="Autoupdate log")
# parser.add_argument("--shed", help="Location of .shed.yml file input.")
parser.add_argument("--out", help="Output file.")
parser.add_argument("--changelog", help="Changelog location")
args = parser.parse_args()

text = []
new_changelog_lines = []
release_line = None

text.append(
    f"Hello! This is an automated update of the following workflow: **{args.repo}**. I created this PR because I think one or more of the component tools are out of date, i.e. there is a newer version available on the ToolShed.\n"
)
text.append(
    "By comparing with the latest versions available on the ToolShed, it seems the following tools are outdated:"
)

with open(args.log) as f:
    already_reported = {}
    for line in f.readlines():
        if " -> " in line:
            words = line.split()
            from_version = words[1]
            to_version = words[3]
            if to_version not in already_reported.get(from_version, []):
                text.append(f"* `{from_version}` should be updated to `{to_version}`")
                new_changelog_lines.append(
                    f"- `{from_version}` was updated to `{to_version}`"
                )
                already_reported[from_version] = already_reported.get(from_version, []) + [to_version]
        if "The workflow release number has been updated" in line:
            release_line = line
            text.append(f"\n{release_line}")

# Add info on the strategy
text.append("\nIf you want to skip this change, close this PR without deleting the branch. It will be reopened if another change is detected.")
text.append("Any commit from another author than 'planemo-autoupdate' will prevent more auto-updates.")
text.append("To ignore manual changes and allow autoupdates, delete the branch.")

with open(args.out, "w") as f:
    f.write("\n".join(text))

if release_line:
    with open(args.changelog, "r+") as f:
        lines = f.readlines()
        new_change = [
            f"## [{release_line.split(' to ')[-1].strip().strip('.')}] - "
            + str(date.today()),
            "",
            "### Automatic update",
        ] + new_changelog_lines
        new_lines = [lines[0]] + new_change + ["".join(lines[1:])]
        f.seek(0)
        f.write("\n".join(new_lines))
    print(
        f"Updating {args.repo} {release_line.split('updated ')[-1].strip().strip('.')}"
    )
else:
    print(f"Updating {args.repo}")
