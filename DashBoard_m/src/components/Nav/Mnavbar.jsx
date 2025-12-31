import { Bell } from "lucide-react";

const Mnavbar = () => {
  return (
    <div className="flex items-center justify-between bg-white shadow-sm px-8 py-3 rounded-xl mb-6">
      <h2 className="text-xl font-semibold text-gray-800">Member Dashboard</h2>

      <div className="flex items-center gap-6">
        <Bell className="text-gray-500 cursor-pointer hover:text-[#6B5AED]" />

        <div className="flex items-center gap-3">
          <img
            src="https://i.pravatar.cc/40"
            alt="Profile"
            className="w-10 h-10 rounded-full"
          />
          <div className="text-sm">
            <p className="font-medium text-gray-700">Sarah Johnson</p>
            <p className="text-xs text-gray-500">Verified Member</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Mnavbar;
