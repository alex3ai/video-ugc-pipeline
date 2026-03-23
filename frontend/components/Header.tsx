import Link from 'next/link';

const Header = () => {
  return (
    <header className="bg-white shadow-sm py-4">
      <div className="container mx-auto px-4 flex justify-between items-center">
        <Link href="/" className="text-xl font-bold text-blue-600">
          Video UGC Pipeline
        </Link>
        <nav>
          <ul className="flex space-x-6">
            <li>
              <Link href="/" className="text-gray-700 hover:text-blue-600 transition-colors">
                Nova Campanha
              </Link>
            </li>
            <li>
              <Link href="/campaigns" className="text-gray-700 hover:text-blue-600 transition-colors">
                Campanhas
              </Link>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;