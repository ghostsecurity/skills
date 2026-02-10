#!/bin/bash
# install-wraith.sh
# Cross-platform installer for the wraith SCA scanner
# Supports: Linux (amd64, arm64), macOS (amd64, arm64), Windows (amd64 via Git Bash/WSL)

set -e

# Configuration
REPO="ghostsecurity/wraith"
BIN_DIR="${HOME}/.ghost/bin"
BINARY_NAME="wraith"
LOCAL_FALLBACK_DIR="${HOME}/.ghost/releases/latest"

# Detect platform
detect_platform() {
    local os arch

    # Detect OS
    case "$(uname -s)" in
        Linux*)     os="linux" ;;
        Darwin*)    os="darwin" ;;
        MINGW*|MSYS*|CYGWIN*)  os="windows" ;;
        *)          echo "Unsupported OS: $(uname -s)" >&2; exit 1 ;;
    esac

    # Detect architecture
    case "$(uname -m)" in
        x86_64|amd64)   arch="amd64" ;;
        aarch64|arm64)  arch="arm64" ;;
        *)              echo "Unsupported architecture: $(uname -m)" >&2; exit 1 ;;
    esac

    echo "${os}_${arch}"
}

# Get latest release version
get_latest_version() {
    curl -s "https://api.github.com/repos/${REPO}/releases/latest" | \
        grep '"tag_name":' | \
        sed -E 's/.*"([^"]+)".*/\1/'
}

# Check if wraith is already installed and get version
get_installed_version() {
    if [ -x "${BIN_DIR}/${BINARY_NAME}" ]; then
        "${BIN_DIR}/${BINARY_NAME}" version 2>/dev/null | head -1 || echo ""
    else
        echo ""
    fi
}

# Install from local fallback directory
install_from_local() {
    local platform="$1"
    local os="${platform%_*}"
    local arch="${platform#*_}"
    local ext="tar.gz"
    local local_file

    # Windows uses zip
    if [ "$os" = "windows" ]; then
        ext="zip"
        BINARY_NAME="wraith.exe"
    fi

    local_file="${LOCAL_FALLBACK_DIR}/wraith_${os}_${arch}.${ext}"

    if [ ! -f "$local_file" ]; then
        echo "Local fallback not found: ${local_file}" >&2
        return 1
    fi

    echo "Installing from local fallback: ${local_file}"

    # Create bin directory
    mkdir -p "${BIN_DIR}"

    # Extract
    local tmp_dir
    tmp_dir=$(mktemp -d)
    trap "rm -rf ${tmp_dir}" EXIT

    if [ "$ext" = "zip" ]; then
        unzip -q "${local_file}" -d "${tmp_dir}"
    else
        tar xzf "${local_file}" -C "${tmp_dir}"
    fi

    # Install wraith binary
    mv "${tmp_dir}/${BINARY_NAME}" "${BIN_DIR}/${BINARY_NAME}"
    chmod +x "${BIN_DIR}/${BINARY_NAME}"

    # Install osv-scanner if present (bundled with wraith)
    if [ -f "${tmp_dir}/osv-scanner" ]; then
        mv "${tmp_dir}/osv-scanner" "${BIN_DIR}/osv-scanner"
        chmod +x "${BIN_DIR}/osv-scanner"
    elif [ -f "${tmp_dir}/osv-scanner.exe" ]; then
        mv "${tmp_dir}/osv-scanner.exe" "${BIN_DIR}/osv-scanner.exe"
        chmod +x "${BIN_DIR}/osv-scanner.exe"
    fi

    # macOS: remove quarantine attribute
    if [ "$os" = "darwin" ]; then
        xattr -d com.apple.quarantine "${BIN_DIR}/${BINARY_NAME}" 2>/dev/null || true
        xattr -d com.apple.quarantine "${BIN_DIR}/osv-scanner" 2>/dev/null || true
    fi

    echo "Installed to: ${BIN_DIR}/${BINARY_NAME}"
    return 0
}

# Download and install from GitHub
install_from_github() {
    local platform="$1"
    local version="$2"
    local os="${platform%_*}"
    local arch="${platform#*_}"
    local ext="tar.gz"
    local download_url

    # Windows uses zip
    if [ "$os" = "windows" ]; then
        ext="zip"
        BINARY_NAME="wraith.exe"
    fi

    # Construct download URL
    download_url="https://github.com/${REPO}/releases/download/${version}/wraith_${os}_${arch}.${ext}"

    echo "Downloading wraith ${version} for ${platform}..."
    echo "URL: ${download_url}"

    # Create bin directory
    mkdir -p "${BIN_DIR}"

    # Download and extract
    local tmp_dir
    tmp_dir=$(mktemp -d)
    trap "rm -rf ${tmp_dir}" EXIT

    if [ "$ext" = "zip" ]; then
        curl -sfL "${download_url}" -o "${tmp_dir}/wraith.zip" || return 1
        unzip -q "${tmp_dir}/wraith.zip" -d "${tmp_dir}"
    else
        curl -sfL "${download_url}" -o "${tmp_dir}/wraith.tar.gz" || return 1
        tar xzf "${tmp_dir}/wraith.tar.gz" -C "${tmp_dir}"
    fi

    # Install wraith binary
    mv "${tmp_dir}/${BINARY_NAME}" "${BIN_DIR}/${BINARY_NAME}"
    chmod +x "${BIN_DIR}/${BINARY_NAME}"

    # Install osv-scanner if present (bundled with wraith)
    if [ -f "${tmp_dir}/osv-scanner" ]; then
        mv "${tmp_dir}/osv-scanner" "${BIN_DIR}/osv-scanner"
        chmod +x "${BIN_DIR}/osv-scanner"
    elif [ -f "${tmp_dir}/osv-scanner.exe" ]; then
        mv "${tmp_dir}/osv-scanner.exe" "${BIN_DIR}/osv-scanner.exe"
        chmod +x "${BIN_DIR}/osv-scanner.exe"
    fi

    # macOS: remove quarantine attribute
    if [ "$os" = "darwin" ]; then
        xattr -d com.apple.quarantine "${BIN_DIR}/${BINARY_NAME}" 2>/dev/null || true
        xattr -d com.apple.quarantine "${BIN_DIR}/osv-scanner" 2>/dev/null || true
    fi

    echo "Installed to: ${BIN_DIR}/${BINARY_NAME}"
    return 0
}

# Main
main() {
    echo "Wraith SCA Scanner Installer"
    echo "============================"

    # Detect platform
    local platform
    platform=$(detect_platform)
    echo "Platform: ${platform}"

    # Check if already installed
    local installed_version
    installed_version=$(get_installed_version)
    echo "Installed version: ${installed_version:-none}"

    if [ -n "$installed_version" ]; then
        echo "Already installed!"
        echo "Binary path: ${BIN_DIR}/${BINARY_NAME}"
        exit 0
    fi

    # Try GitHub first
    local latest_version
    latest_version=$(get_latest_version)

    if [ -n "$latest_version" ]; then
        echo "Latest version: ${latest_version}"
        if install_from_github "$platform" "$latest_version"; then
            echo ""
            echo "Verification:"
            "${BIN_DIR}/${BINARY_NAME}" version
            echo ""
            echo "Installation complete!"
            echo "Binary path: ${BIN_DIR}/${BINARY_NAME}"
            exit 0
        fi
        echo "GitHub download failed, trying local fallback..."
    else
        echo "Could not fetch latest version from GitHub (network error or repo not accessible)"
        echo "Trying local fallback..."
    fi

    # Fallback to local directory
    if install_from_local "$platform"; then
        echo ""
        echo "Verification:"
        "${BIN_DIR}/${BINARY_NAME}" version
        echo ""
        echo "Installation complete (from local fallback)!"
        echo "Binary path: ${BIN_DIR}/${BINARY_NAME}"
        exit 0
    fi

    echo ""
    echo "ERROR: Could not install wraith."
    echo "Please either:"
    echo "  1. Ensure network access to github.com/ghostsecurity/wraith, or"
    echo "  2. Place release artifacts in: ${LOCAL_FALLBACK_DIR}/"
    exit 1
}

main "$@"
