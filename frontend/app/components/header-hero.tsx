import Image from 'next/image'
import Link from 'next/link'
export default function Header() {
  return (
    <header className="flex justify-around items-center  bg-white text-black shadow-sm hover:shadow-md transition-shadow">
      <section className="flex items-center space-x-4">
        <h1 className="sr-only">Trello</h1>
        <Link href="/">
          <Image src="/logo.svg" alt="App Logo" width={112} height={112} />
        </Link>
        <nav className="text-gray-700">
          <ul className="flex space-x-6 ml-8 ">
            <li className="hover:text-blue-500">
              <Link href="/">Home</Link>
            </li>
            <li className="hover:text-blue-500">
              <Link
                href="https://github.com/tomy08/trello_clone"
                target="_blank"
              >
                About (Github)
              </Link>
            </li>
          </ul>
        </nav>
      </section>
      <nav>
        <ul className="flex items-center justify-center space-x-4">
          <li className="text-lg text-gray-800">
            <Link href="/login">Log in</Link>
          </li>
          <li className="bg-blue-600 text-white p-5 hover:bg-blue-700 transition-colors">
            <Link href="/signup">Get Trello for free</Link>
          </li>
        </ul>
      </nav>
    </header>
  )
}
