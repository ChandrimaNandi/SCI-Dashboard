import java.sql.*;
import java.util.*;
class Customer_info
{
    //adds a new customer to the database
    static void addCustomer(Connection conn, int customer_id, String name, String phone_no, String email) throws SQLException
    {
        String query = "INSERT INTO customer_info VALUES(?, ?, ?, ?)"; //query to insert a new customer
        PreparedStatement stmt = conn.prepareStatement(query);//create a prepared statement
        stmt.setInt(1, customer_id);//set the customer_id
        stmt.setString(2, name);//set the name
        stmt.setString(3, phone_no);//set the phone_no
        stmt.setString(4, email);//set the email
        stmt.executeUpdate();//execute the query
        System.out.println("Customer added successfully");
        conn.commit(); //commit the transaction
    }
    //removes a customer from the database
    static void deleteCustomer(Connection conn, int customer_id) throws SQLException
    {
        String query = "DELETE FROM customer_info WHERE customer_id = ?";
        PreparedStatement stmt = conn.prepareStatement(query);
        stmt.setInt(1, customer_id);
        stmt.executeUpdate();
        System.out.println("Customer deleted successfully");
        conn.commit();
    }
    //lists the details of a customer
    static void viewcustomerdetails(Connection conn, int customer_id) throws SQLException
    {
        String query = "SELECT * FROM customer_info WHERE customer_id = ?";
        PreparedStatement stmt = conn.prepareStatement(query);
        stmt.setInt(1, customer_id);
        ResultSet rs = stmt.executeQuery();
        while(rs.next())
        {
            System.out.println("Customer id: " + rs.getInt("customer_id"));
            System.out.println("Name: " + rs.getString("name"));
            System.out.println("Phone no: " + rs.getString("phone_no"));
            System.out.println("Email: " + rs.getString("email"));
        }
    }
}

class Room_info
{
    //adds a booking to the database
    static void addbooking(Connection conn,String rno) throws SQLException
    {
        String query="UPDATE room_info SET is_available=0 WHERE room_no=?";
        PreparedStatement stmt = conn.prepareStatement(query);
        stmt.setString(1,rno);
        stmt.executeUpdate();
        conn.commit();
    }
    //adds a room in the Database
    // static void addRoom(Connection conn, int room_no, String room_type, int price) throws SQLException
    // {
    //     String query = "INSERT INTO room_info VALUES(?, ?, ?)";
    //     PreparedStatement stmt = conn.prepareStatement(query);
    //     stmt.setInt(1, room_no);
    //     stmt.setString(2, room_type);
    //     stmt.setInt(3, price);
    //     stmt.executeUpdate();
    //     System.out.println("Room added successfully");
    //     conn.commit();
    // }
    // static void deleteRoom(Connection conn, int room_no) throws SQLException
    // {
    //     String query = "DELETE FROM room_info WHERE room_no = ?";
    //     PreparedStatement stmt = conn.prepareStatement(query);
    //     stmt.setInt(1, room_no);
    //     stmt.executeUpdate();
    //     System.out.println("Room deleted successfully");
    //     conn.commit();
    // }

    //lists all the available rooms
    static void listavailableRooms(Connection conn) throws SQLException
    {
        String query = "SELECT * FROM room_info WHERE is_available = 1";
        PreparedStatement stmt = conn.prepareStatement(query);
        ResultSet rs = stmt.executeQuery();
        System.out.println("Available rooms are:");
        while(rs.next())
        {
            System.out.println("Room no: " + rs.getString("room_no"));
            System.out.println("Price per night: " + rs.getInt("price_per_night"));
        }
    }
    //to update the room price
    static void updateRoomPrice(Connection conn, String room_no, String price_per_night) throws SQLException
    {
        String query = "UPDATE room_info SET price_per_night = ? WHERE room_no = ?";
        PreparedStatement stmt = conn.prepareStatement(query);
        stmt.setString(1, price_per_night);
        stmt.setString(2, room_no);
        stmt.executeUpdate();
        System.out.println("Price updated successfully");
        conn.commit();
    }
    
}

class Booking_status
{
    //adds a booking to the database
    static void addBooking(Connection conn, int customer_id,int booking_id, int paid) throws SQLException
    {
        String query = "INSERT INTO booking_status VALUES(?, ?,?)";
        PreparedStatement stmt = conn.prepareStatement(query);
        stmt.setInt(1, customer_id);
        stmt.setInt(2, booking_id);
        stmt.setInt(3, paid);
        stmt.executeUpdate();
        conn.commit();
       // System.out.println("Booking added successfully");
    }
    //to remove a booking
    static void removebooking(Connection conn,int booking_id) throws SQLException
    {
        String query = "DELETE FROM booking_status WHERE booking_id = ?";
        PreparedStatement stmt = conn.prepareStatement(query);
        stmt.setInt(1, booking_id);
        stmt.executeUpdate();
        conn.commit();
        //System.out.println("Booking removed successfully");
    }

}

class Booking_info
{
    //update the room no of the booking
    static void updateroomno(Connection conn,int booking_id, String new_room_no) throws SQLException
    {
        
        //change the is_available status of the both rooms
        String query1 = "UPDATE room_info SET is_available = 1 WHERE room_no = (SELECT room_no FROM booking_info WHERE booking_id = ?)";
        PreparedStatement stmt1 = conn.prepareStatement(query1);
        stmt1.setInt(1, booking_id);
        stmt1.executeUpdate();
        String query = "UPDATE booking_info SET room_no = ? WHERE booking_id = ?";
        PreparedStatement stmt = conn.prepareStatement(query);
        stmt.setString(1, new_room_no);
        stmt.setInt(2, booking_id);
        stmt.executeUpdate();
        String query2 = "UPDATE room_info SET is_available = 0 WHERE room_no = ?";
        PreparedStatement stmt2 = conn.prepareStatement(query2);
        stmt2.setString(1, new_room_no);
        stmt2.executeUpdate();
        conn.commit();
        System.out.println("Room no updated successfully");
    }

    //getting the booking_id based on the customer_id
    static int getbookingid(Connection conn,int customer_id) throws SQLException
    {
        String query = "SELECT booking_id FROM booking_status WHERE customer_id = ?";
        PreparedStatement stmt = conn.prepareStatement(query);
        stmt.setInt(1, customer_id);
        ResultSet rs = stmt.executeQuery();
        int booking_id = 0;
        while(rs.next())
        {
            booking_id = rs.getInt("booking_id");
        }
        return booking_id;
    }

    //to add a booking
    static void addBooking(Connection conn, int booking_id, String check_in, String check_out,String room_no) throws SQLException
    {
        String query = "INSERT INTO booking_info VALUES(?, ?, ?, ?)";
        PreparedStatement stmt = conn.prepareStatement(query);
        stmt.setInt(1, booking_id);
        stmt.setString(2, check_in);
        stmt.setString(3, check_out);
        stmt.setString(4, room_no);
        stmt.executeUpdate();
        System.out.println("Booking added successfully with booking id: " + booking_id);
        conn.commit();
    }

    
    //remove a booking
    static void removebooking(Connection conn, int booking_id) throws SQLException
    {
        String query = "DELETE FROM booking_info WHERE booking_id = ?";
        PreparedStatement stmt = conn.prepareStatement(query);
        stmt.setInt(1, booking_id);
        stmt.executeUpdate();
        System.out.println("Booking removed successfully");
        conn.commit();
    }
    //view booking details
    static void viewbookingdetails(Connection conn,int booking_id)throws SQLException
    {
        String query= "SELECT b.booking_id, b.checkin_date, b.checkout_date, b.room_no, s.paid, r.price_per_night FROM booking_info b INNER JOIN booking_status s ON s.booking_id = b.booking_id INNER JOIN room_info r ON r.room_no = b.room_no WHERE b.booking_id = ?;";
        PreparedStatement stmt = conn.prepareStatement(query);
        stmt.setInt(1, booking_id);
        ResultSet rs = stmt.executeQuery();
        System.out.println("Booking details are:");
        while(rs.next())
        {
            System.out.println("Booking id: "+rs.getString(1));
            System.out.println("Check in: "+rs.getString(2));
            System.out.println("Check out: "+rs.getString(3));
            System.out.println("Room no: "+rs.getString(4));
            System.out.println("Room price per night: "+rs.getString(6));
            System.out.println("Paid: "+rs.getInt(5));
        }
    }
    //lists all the bookings with same check in and check out date
    static void samechckinchckout(Connection conn) throws SQLException
    {
        String query = "SELECT bi.booking_id,bi.room_no,c.name FROM booking_info bi  JOIN booking_status s ON bi.booking_id = s.booking_id JOIN customer_info c ON s.customer_id = c.customer_id WHERE checkin_date =checkout_date";
        PreparedStatement stmt = conn.prepareStatement(query);
        ResultSet rs = stmt.executeQuery();
        System.out.println("Bookings with same check in and check out date are:");
        while(rs.next())
        {
            System.out.println("Customer name: " + rs.getString("name"));
            System.out.println("Booking id: " + rs.getInt("booking_id"));
            System.out.println("Room no: " + rs.getString("room_no"));
        }
    }

    //lists all the bookings with stay duration more than a week
    static void morethanaweek(Connection conn) throws SQLException
    {
        String query = "SELECT bi.booking_id,bi.room_no,c.name FROM booking_info bi  JOIN booking_status s ON bi.booking_id = s.booking_id JOIN customer_info c ON s.customer_id = c.customer_id WHERE DATEDIFF(checkout_date, checkin_date) > 7";
        PreparedStatement stmt = conn.prepareStatement(query);
        ResultSet rs = stmt.executeQuery();
        System.out.println("Bookings with stay duration more than a week are:");
        while(rs.next())
        {
            System.out.println("Customer name: " + rs.getString("name"));
            System.out.println("Booking id: " + rs.getInt("booking_id"));
            System.out.println("Room no: " + rs.getString("room_no"));
        }
    }
}
class Payment_info
{
    //getting the room cost
    static double roomcost(Connection conn, int booking_id) throws SQLException
    {
        String query = "SELECT price_per_night FROM room_info WHERE room_no = (SELECT room_no FROM booking_info WHERE booking_id = ?)";
        PreparedStatement stmt = conn.prepareStatement(query);
        stmt.setInt(1, booking_id);
        ResultSet rs = stmt.executeQuery();
        rs.next();
        double price = Double.parseDouble(rs.getString("price_per_night"));
        return price;
    }
    //getting the amount to be paid
    static double amounttobepaid(Connection conn, int booking_id) throws SQLException
    {
        double price = roomcost(conn, booking_id);
        String query = "SELECT DATEDIFF(checkout_date, checkin_date) FROM booking_info WHERE booking_id = ?";
        PreparedStatement stmt = conn.prepareStatement(query);
        stmt.setInt(1, booking_id);
        ResultSet rs = stmt.executeQuery();
        rs.next();
        int days = rs.getInt(1)+1;
        double amount = price * days;
        return amount;
    }

    //to show all the paid bookings
    static void showallpaid(Connection conn) throws SQLException
    {
        String query = "SELECT * FROM booking_info WHERE booking_id IN (SELECT booking_id FROM booking_status WHERE paid = 1)";
        PreparedStatement stmt = conn.prepareStatement(query);
        ResultSet rs = stmt.executeQuery();
        System.out.println("All the paid bookings are:");
        while(rs.next())
        {
            System.out.println("Booking id: " + rs.getInt("booking_id"));
            System.out.println("Room no: " + rs.getString("room_no"));
        }
    }

    //to show all the due bookings
    static void showalldue(Connection conn) throws SQLException
    {
        String query = "SELECT b.booking_id, b.room_no, c.name FROM booking_info b JOIN booking_status s ON b.booking_id=s.booking_id JOIN customer_info c ON s.customer_id=c.customer_id WHERE b.booking_id IN (SELECT booking_id FROM booking_status WHERE paid = 0)";
        PreparedStatement stmt = conn.prepareStatement(query);
        ResultSet rs = stmt.executeQuery();
        System.out.println("All the due bookings are:");
        while(rs.next())
        {
            System.out.println("Customer name: " + rs.getString("name"));
            System.out.println("Booking id: " + rs.getInt("booking_id"));
            System.out.println("Room no: " + rs.getString("room_no"));
        }
    }
    //to update the payment_info after a payment
    static void updatePayTable(Connection conn,int payment_id,int booking_id, String paymode ,String amt) throws SQLException
    {
        String query = "INSERT INTO payment_info VALUES(?,?,?,?)";
        PreparedStatement stmt = conn.prepareStatement(query);
        stmt.setInt(1, payment_id);
        stmt.setInt(2, booking_id);
        stmt.setString(3, paymode);
        stmt.setString(4,String.valueOf(amounttobepaid(conn, booking_id)));
        stmt.executeUpdate();
        query="UPDATE booking_status SET paid=1 WHERE booking_id=?";
        stmt = conn.prepareStatement(query);
        stmt.setInt(1, booking_id);
        stmt.executeUpdate();
        query="UPDATE room_info SET is_available=1 WHERE room_no=(SELECT room_no FROM booking_info WHERE booking_id=?)";
        stmt = conn.prepareStatement(query);
        stmt.setInt(1, booking_id);
        stmt.executeUpdate();
        System.out.println("Payment done successfully");
        conn.commit();

    }
   
}

public class imt2022062_HotelBookings {

   // Set JDBC driver name and database URL
   static final String JDBC_DRIVER = "com.mysql.cj.jdbc.Driver";
   static final String DB_URL = "jdbc:mysql://localhost:3306/HotelBookings?useSSL=false";

   // Database credentials
   static final String USER = "root";// add your user
   static final String PASSWORD = "admin";// add password
   static String[] menuOptions = {
    "0.  Show the menu",
    "1.  Add a customer",
    "2.  Add a booking",
    "3.  Remove a booking",
    "4.  Remove a customer",
    "5.  Update room price",
    "6.  Update room number",
    "7.  Amount to be paid",
    "8.  Show all the paid bookings",
    "9.  List all the due bookings",
    "10. List all the rooms available",
    "11. View details of a booking",
    "12. View details of a customer",
    "13. Show all the bookings with same check in and check out date",
    "14. Show all the bookings booked for more than a week",
    "15. Exit"
};

// Calculate the number of spaces needed to center "MENU"
static int consoleWidth = 80; // Adjust as per your console width
static int menuWidth = 4 + 26 + 4; // Length of "MENU" plus surrounding spaces
static int spaces = (consoleWidth - menuWidth) / 2;
static void menuprint()
{
    // Display menu with "MENU" centered
    //System.out.println(" ".repeat(spaces) + "WELCOME" + " ".repeat(spaces));
    System.out.println(" ".repeat(spaces) + "MENU" + " ".repeat(spaces));
    for (int i = 0; i < menuOptions.length; i++) {
        System.out.println(menuOptions[i]);
}
}
   public static void main(String[] args) {
    Connection conn = null;
    Statement stmt = null;
    Scanner sc = new Scanner(System.in);
    // STEP 2. Connecting to the Database
    try 
    {
        // STEP 2a: Register JDBC driver
        Class.forName(JDBC_DRIVER);
        // STEP 2b: Open a connection
        System.out.println("Connecting to database...");
        conn = DriverManager.getConnection(DB_URL, USER, PASSWORD);
        //set autocommit to false
        conn.setAutoCommit(false);
        stmt=conn.createStatement();
        String[] query={"SELECT max(customer_id)+1 from customer_info","SELECT max(booking_id)+1 from booking_info","SELECT max(payment_id)+1 from payment_info"};
        int a[]=new int[3];
        for(int i=0;i<3;i++)
        {
            ResultSet rs=stmt.executeQuery(query[i]);
            rs.next();
            a[i]=rs.getInt(1);
        }

        menuprint();
        
        System.out.println("Enter your choice: ");
        int che = sc.nextInt();
        while(true)
        {
            String[] ip;
            sc.nextLine();
            switch(che)
            {
                case 1:
                    System.out.println("Enter full name, phone number, email: ");
                    ip = sc.nextLine().split(" ");
                    Customer_info.addCustomer(conn, a[0]++, ip[0],ip[1],ip[2]);
                    break;
                case 2:
                    System.out.println("Enter customerid, check in date, check out date, room number: ");
                    ip = sc.nextLine().split(" ");
                    a[1]++;
                    Booking_status.addBooking(conn,Integer.parseInt(ip[0]),a[1], 0);
                    Booking_info.addBooking(conn,a[1], ip[1], ip[2], ip[3]);
                    Room_info.addbooking(conn,ip[3]);
                    
                    break;
                case 3:
                    System.out.println("Enter booking id: ");
                    int booking_id = sc.nextInt();
                    Booking_info.removebooking(conn, booking_id);
                    Booking_status.removebooking(conn, booking_id);
                    break;
                case 4:
                    System.out.println("Enter customer id: ");
                    int customer_id = sc.nextInt();
                    
                    int booking_id1 = Booking_info.getbookingid(conn, customer_id);
                    Customer_info.deleteCustomer(conn, customer_id);
                    Booking_info.removebooking(conn, booking_id1);
                    Booking_status.removebooking(conn, booking_id1);
                    break;
                case 5:
                    System.out.println("Enter room number new price: ");
                    ip = sc.nextLine().split(" ");
                    Room_info.updateRoomPrice(conn, ip[0],ip[1]);
                    break;
                case 6:
                    System.out.println("Enter booking_id, new room number: ");
                    ip = sc.nextLine().split(" ");
                    Booking_info.updateroomno(conn, Integer.parseInt(ip[0]), ip[1]);
                    break;
                case 7:
                    System.out.println("Enter booking id and paymentmode: ");
                    ip=sc.nextLine().split(" ");
                    int booking_id2 = Integer.parseInt(ip[0]);
                    String paymode=ip[1];
                    System.out.println("Amount to be paid: "+Payment_info.amounttobepaid(conn, booking_id2));
                    Payment_info.updatePayTable(conn,a[2]++, booking_id2, paymode, String.valueOf(Payment_info.amounttobepaid(conn, booking_id2)));
                    break;
                case 8:
                    Payment_info.showallpaid(conn);
                    break;
                case 9:
                    Payment_info.showalldue(conn);
                    break;
                case 10:
                    Room_info.listavailableRooms(conn);
                    break;
                case 11:
                    System.out.println("Enter booking id: ");
                    int booking_id3 = sc.nextInt();
                    Booking_info.viewbookingdetails(conn, booking_id3);
                    break;
                case 12:
                    System.out.println("Enter customer id: ");
                    int customer_id1 = sc.nextInt();
                    Customer_info.viewcustomerdetails(conn, customer_id1);
                    break;
                case 13:
                    // System.out.println("Enter check in date, check out date: ");
                    // ip = sc.nextLine().split(" ");
                    Booking_info.samechckinchckout(conn);
                    break;
                case 14:
                    Booking_info.morethanaweek(conn);
                    break; 

            
                case 15:
                            System.out.println("Exiting from the booking system...");
                            try {
                                if(stmt!=null) {
                                    stmt.close();
                                }
                            }
                            catch(SQLException se) {
                                se.printStackTrace();
                            }
                            System.exit(0);
                            break;
                        case 0:
                            menuprint();
                            System.out.println("Enter choice: ");
                            che = sc.nextInt();
                            continue;
                        default:
                            System.out.println("Invalid choice");

            }
            System.out.println("Enter your choice or choose 0 to show menu: ");
            che = sc.nextInt();
        }
    }
    catch(SQLException se){
        //Handle errors for JDBC
        se.printStackTrace();
        // If there is an error then rollback the changes.
        System.out.println("Rolling back data here....");
        try{
           if(conn!=null)
               conn.rollback();
        }catch(SQLException se2){
            System.out.println("Rollback failed....");
                se2.printStackTrace();
        }
     }catch(Exception e){
        //Handle errors for Class.forName
        e.printStackTrace();
     }finally{
        //finally block used to close resources
        try{
           if(stmt!=null)
              stmt.close();
        }catch(SQLException se2){
        }// nothing we can do
        try{
           if(conn!=null)
              conn.close();
        }catch(SQLException se){
           se.printStackTrace();
        }//end finally try
     }//end try
        System.out.println("Hope you had a good experience!");
    }
}