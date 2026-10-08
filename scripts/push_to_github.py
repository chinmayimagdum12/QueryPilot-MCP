"""Helper script to push QueryPilot MCP to GitHub using a Personal Access Token."""

import sys
import dulwich.porcelain as porcelain


def push():
    print("=" * 55)
    print(" QueryPilot MCP - GitHub Push Utility")
    print(" Target: https://github.com/chinmayimagdum12/QueryPilot-MCP.git")
    print("=" * 55)

    if len(sys.argv) > 1:
        token = sys.argv[1].strip()
    else:
        token = input("\nEnter your GitHub Personal Access Token: ").strip()

    if not token:
        print("Error: No GitHub token provided.")
        sys.exit(1)

    url = f"https://{token}@github.com/chinmayimagdum12/QueryPilot-MCP.git"
    print("\nPushing 'main' branch to GitHub...")

    try:
        porcelain.push(".", url, "refs/heads/main")
        print("\n" + "=" * 55)
        print(" SUCCESS: Code successfully pushed to GitHub!")
        print(" Repository: https://github.com/chinmayimagdum12/QueryPilot-MCP")
        print("=" * 55)
    except Exception as e:
        print(f"\nPush failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Verify the token has the 'repo' (Full control of private repositories) scope.")
        print("2. Ensure you have write permissions to 'chinmayimagdum12/QueryPilot-MCP'.")


if __name__ == "__main__":
    push()
