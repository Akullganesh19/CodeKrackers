/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['three', '@react-three/fiber', '@react-three/drei'],
  // Force webpack and disable some experimental features that might cause the usize error on Windows
  webpack: (config) => {
    return config
  },
}

export default nextConfig
