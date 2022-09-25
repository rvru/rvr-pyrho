scripts_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Adding $scripts_dir to PATH"
export PATH=${PATH}:${scripts_dir}
