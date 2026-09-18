import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const CostingApp());
}

class MarkaziaColors {
  static const Color orange = Color(0xFFFF9C00); // لون المركزية المعتمد #FF9C00
  static const Color dark = Color(0xFF18181B);   // فحمى داكن متناسق مع الشعار الشفاف
  static const Color bg = Color(0xFFFBF9F5);     // خلفية كريمية مريحة
}

class CostingApp extends StatelessWidget {
  const CostingApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'المركزية - نظام التكاليف الموحد',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        fontFamily: 'Segoe UI',
        scaffoldBackgroundColor: MarkaziaColors.bg,
        colorScheme: ColorScheme.fromSeed(
          seedColor: MarkaziaColors.orange,
          primary: MarkaziaColors.orange,
          secondary: MarkaziaColors.orange,
          surface: Colors.white,
          brightness: Brightness.light,
        ),
      ),
      home: const Directionality(
        textDirection: TextDirection.rtl,
        child: MainHubScreen(),
      ),
    );
  }
}

void copyCode(BuildContext context, String code, String label) {
  if (code.isEmpty || code.toLowerCase() == 'nan') return;
  Clipboard.setData(ClipboardData(text: code));
  ScaffoldMessenger.of(context).hideCurrentSnackBar();
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Row(
        children: [
          const Icon(Icons.check_circle_rounded, color: MarkaziaColors.orange, size: 20),
          const SizedBox(width: 8),
          Text('تم نسخ $label: $code', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        ],
      ),
      backgroundColor: MarkaziaColors.dark,
      duration: const Duration(seconds: 2),
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      width: 320,
    ),
  );
}

Widget buildCopyBadge(BuildContext context, {required String label, required String code, Color? color}) {
  if (code.isEmpty || code.toLowerCase() == 'nan') return const SizedBox.shrink();
  final c = color ?? MarkaziaColors.orange;
  return InkWell(
    onTap: () => copyCode(context, code, label),
    borderRadius: BorderRadius.circular(8),
    child: Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
      decoration: BoxDecoration(
        color: c.withOpacity(0.09),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: c.withOpacity(0.35)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text('$label: $code', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: c)),
          const SizedBox(width: 5),
          Icon(Icons.copy_rounded, size: 12, color: c),
        ],
      ),
    ),
  );
}

class MainHubScreen extends StatefulWidget {
  const MainHubScreen({super.key});

  @override
  State<MainHubScreen> createState() => _MainHubScreenState();
}

class _MainHubScreenState extends State<MainHubScreen> {
  int _selectedTabIndex = 0;
  List<dynamic> _recipes = [];
  List<dynamic> _staffMeals = [];
  List<dynamic> _talabatSheets = [];
  List<dynamic> _odooCatalog = [];
  final Map<String, String> _odooIndex = {};
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadAllDatabases();
  }

  Future<void> _loadAllDatabases() async {
    try {
      final rStr = await rootBundle.loadString('assets/data/costing_data.json');
      final sStr = await rootBundle.loadString('assets/data/staff_meals.json');
      final tStr = await rootBundle.loadString('assets/data/talabat_mart.json');
      final oStr = await rootBundle.loadString('assets/data/odoo_catalog.json');

      final oList = json.decode(oStr) as List;
      for (var it in oList) {
        final c = (it['code'] ?? '').toString().trim().toLowerCase();
        final n = (it['name'] ?? '').toString().trim();
        if (c.isNotEmpty && n.isNotEmpty) {
          _odooIndex[c] = n;
        }
      }

      setState(() {
        _recipes = json.decode(rStr);
        _staffMeals = json.decode(sStr);
        _talabatSheets = json.decode(tStr);
        _odooCatalog = oList;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  String getOdooOfficialName(String code, String fallbackName) {
    final c = code.trim().toLowerCase();
    if (_odooIndex.containsKey(c)) {
      return _odooIndex[c]!;
    }
    return fallbackName;
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator(color: MarkaziaColors.orange)),
      );
    }

    return Scaffold(
      appBar: AppBar(
        toolbarHeight: 68,
        elevation: 0,
        title: Row(
          children: [
            Image.asset(
              'assets/logo.png',
              height: 48,
              fit: BoxFit.contain,
              errorBuilder: (_, __, ___) => const Icon(Icons.restaurant_menu, color: MarkaziaColors.orange, size: 34),
            ),
            const SizedBox(width: 14),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: const [
                Text('الـمـركــزيــة  |  AL-MARKAZIA',
                    style: TextStyle(fontWeight: FontWeight.w900, fontSize: 17, color: Colors.white)),
                Text('نظام إدارة وحساب التكاليف الموحد والشامل',
                    style: TextStyle(fontSize: 11, color: Colors.white70)),
              ],
            ),
            const Spacer(),
            // بادج مدير قسم التكاليف (أ. أحمد الخضري) بتصميم راقي ومتناسق
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(0.35),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: MarkaziaColors.orange.withOpacity(0.6), width: 1.2),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: const [
                  Icon(Icons.workspace_premium_rounded, color: MarkaziaColors.orange, size: 18),
                  SizedBox(width: 8),
                  Text('إدارة: ', style: TextStyle(fontSize: 12, color: Colors.white70)),
                  Text('أ. أحمد الخضري', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white)),
                  SizedBox(width: 6),
                  Text('(مدير قسم التكاليف)', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: MarkaziaColors.orange)),
                ],
              ),
            ),
            const SizedBox(width: 12),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.1),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.white12),
              ),
              child: Text(
                'أودو: ${_odooCatalog.length}  |  طلبات مارت: ${_talabatSheets.length}  |  التكاليف: ${_recipes.length}  |  وجبات الموظفين: ${_staffMeals.length}',
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white70),
              ),
            ),
          ],
        ),
        backgroundColor: MarkaziaColors.dark,
      ),
      body: Row(
        children: [
          // شريط تنقل ذو حجم ثابت ومغلق هندسياً يمنع اهتزاز الشاشة نهائياً
          SizedBox(
            width: 92,
            child: NavigationRail(
              minWidth: 92,
              minExtendedWidth: 92,
              selectedIndex: _selectedTabIndex,
              onDestinationSelected: (index) => setState(() => _selectedTabIndex = index),
              labelType: NavigationRailLabelType.all,
              backgroundColor: Colors.white,
              selectedIconTheme: const IconThemeData(color: MarkaziaColors.orange, size: 28),
              unselectedIconTheme: const IconThemeData(color: Colors.black45),
              selectedLabelTextStyle: const TextStyle(color: MarkaziaColors.orange, fontWeight: FontWeight.bold, fontSize: 11),
              unselectedLabelTextStyle: const TextStyle(color: Colors.black54, fontWeight: FontWeight.bold, fontSize: 11),
              indicatorColor: MarkaziaColors.orange.withOpacity(0.15),
              destinations: const [
                NavigationRailDestination(
                  icon: Icon(Icons.account_tree_outlined),
                  selectedIcon: Icon(Icons.account_tree_rounded),
                  label: Text('شجرة التكاليف'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.restaurant_outlined),
                  selectedIcon: Icon(Icons.restaurant_rounded),
                  label: Text('وجبات الموظفين'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.shopping_bag_outlined),
                  selectedIcon: Icon(Icons.shopping_bag_rounded),
                  label: Text('طلبات مارت'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.inventory_2_outlined),
                  selectedIcon: Icon(Icons.inventory_2_rounded),
                  label: Text('دليل أودو'),
                ),
              ],
            ),
          ),
          const VerticalDivider(width: 1, thickness: 1, color: Color(0xFFE2E8F0)),
          Expanded(
            child: IndexedStack(
              index: _selectedTabIndex,
              children: [
                _buildRecipesTab(),
                _buildStaffMealsTab(),
                _buildTalabatTab(),
                _buildOdooCatalogTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // 1. شجرة التكاليف
  Widget _buildRecipesTab() {
    return _UniversalSearchList(
      items: _recipes,
      titleKey: 'name',
      subtitleBuilder: (item) => 'كود: ${item['code']} | فئة: ${item['category']}',
      costBuilder: (item) => (item['total_cost'] as num).toDouble(),
      marginBuilder: (item) => ((item['food_cost_percentage'] ?? 0.0) as num).toDouble() / 100.0,
      detailBuilder: (item) {
        final ings = item['ingredients'] as List? ?? [];
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Card(
              elevation: 0,
              color: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
                side: const BorderSide(color: Color(0xFFE2E8F0)),
              ),
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(item['name'],
                              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: MarkaziaColors.dark)),
                        ),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text('التكلفة: ${(item['total_cost'] as num).toStringAsFixed(3)} د.أ',
                                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: MarkaziaColors.orange)),
                            Text('سعر البيع: ${(item['selling_price'] as num).toStringAsFixed(3)} د.أ',
                                style: TextStyle(fontSize: 13, color: Colors.grey.shade600)),
                          ],
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 12,
                      runSpacing: 8,
                      children: [
                        buildCopyBadge(context, label: 'كود الطبخة', code: item['code']),
                        if (item['odoo_code'].toString().isNotEmpty)
                          buildCopyBadge(context, label: 'كود أودو', code: item['odoo_code']),
                        Chip(
                          label: Text('نسبة التكلفة: ${item['food_cost_percentage']}%',
                              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                          backgroundColor: const Color(0xFFFFF7ED),
                          side: const BorderSide(color: MarkaziaColors.orange),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            const Text('مكونات الوصفة المعيارية (BOM):',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: MarkaziaColors.dark)),
            const SizedBox(height: 8),
            Expanded(
              child: ListView.builder(
                itemCount: ings.length,
                itemBuilder: (context, idx) {
                  final ing = ings[idx];
                  final isSf = ing['is_semi_finished'] == true;
                  final subs = ing['sub_ingredients'] as List? ?? [];
                  final officialName = getOdooOfficialName(ing['code'] ?? '', ing['name'] ?? '');

                  return Card(
                    elevation: 0,
                    color: isSf ? const Color(0xFFFFFDF8) : Colors.white,
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                      side: BorderSide(color: isSf ? MarkaziaColors.orange.withOpacity(0.4) : const Color(0xFFE2E8F0)),
                    ),
                    child: ListTile(
                      title: Text(officialName, style: const TextStyle(fontWeight: FontWeight.bold)),
                      subtitle: Row(
                        children: [
                          Text('المعياري: ${ing['standard_quantity']}  |  الوحدة: ${(ing['cost_per_unit'] as num).toStringAsFixed(3)} د.أ'),
                          const SizedBox(width: 8),
                          buildCopyBadge(context, label: isSf ? 'SF' : 'RM', code: ing['code']),
                        ],
                      ),
                      trailing: Text('${(ing['total_cost'] as num).toStringAsFixed(3)} د.أ',
                          style: const TextStyle(fontWeight: FontWeight.bold, color: MarkaziaColors.orange)),
                    ),
                  );
                },
              ),
            ),
          ],
        );
      },
    );
  }

  // 2. وجبات الموظفين
  Widget _buildStaffMealsTab() {
    return _UniversalSearchList(
      items: _staffMeals,
      titleKey: 'name',
      isStaffTab: true,
      subtitleBuilder: (item) => '${item['date']} | كود: ${item['code']}',
      costBuilder: (item) => (item['total_cost'] as num).toDouble(),
      detailBuilder: (item) {
        final ings = item['ingredients'] as List? ?? [];
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Card(
              elevation: 0,
              color: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
                side: const BorderSide(color: Color(0xFFE2E8F0)),
              ),
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(item['name'],
                              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: MarkaziaColors.dark)),
                          const SizedBox(height: 6),
                          Row(
                            children: [
                              const Icon(Icons.calendar_today_rounded, size: 14, color: MarkaziaColors.orange),
                              const SizedBox(width: 6),
                              Text('تاريخ الوجبة: ${item['date']}',
                                  style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Colors.black54)),
                              const SizedBox(width: 14),
                              buildCopyBadge(context, label: 'معرف الوجبة', code: item['code']),
                            ],
                          ),
                        ],
                      ),
                    ),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text('${(item['total_cost'] as num).toStringAsFixed(3)} د.أ',
                            style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: MarkaziaColors.orange)),
                        const Text('إجمالي تكلفة الوجبة الفعلية', style: TextStyle(fontSize: 11, color: Colors.grey)),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            const Text('مكونات الطبخة الفعلية ومطابقتها مع دليل أودو:',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: MarkaziaColors.dark)),
            const SizedBox(height: 8),
            Expanded(
              child: ListView.builder(
                itemCount: ings.length,
                itemBuilder: (context, idx) {
                  final ing = ings[idx];
                  final isSf = ing['is_semi_finished'] == true;
                  final subs = ing['sub_ingredients'] as List? ?? [];
                  final officialName = getOdooOfficialName(ing['code'] ?? '', ing['name'] ?? '');

                  return Card(
                    elevation: 0,
                    color: Colors.white,
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                      side: const BorderSide(color: Color(0xFFE2E8F0)),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      child: Row(
                        children: [
                          Container(
                            width: 8, height: 8,
                            decoration: const BoxDecoration(color: MarkaziaColors.orange, shape: BoxShape.circle),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(officialName,
                                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: MarkaziaColors.dark)),
                                const SizedBox(height: 4),
                                Wrap(
                                  spacing: 12,
                                  children: [
                                    Text('الفعلي للطبخة: ${ing['actual_quantity']} ${ing['unit']}',
                                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: MarkaziaColors.orange)),
                                    Text('المعياري: ${ing['standard_quantity']}',
                                        style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
                                    buildCopyBadge(context, label: 'كود', code: ing['code']),
                                  ],
                                ),
                              ],
                            ),
                          ),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              Text('${(ing['total_cost'] as num).toStringAsFixed(3)} د.أ',
                                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: MarkaziaColors.orange)),
                              Text('الوحدة: ${(ing['cost_per_unit'] as num).toStringAsFixed(3)} د.أ',
                                  style: TextStyle(fontSize: 11, color: Colors.grey.shade500)),
                            ],
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        );
      },
    );
  }

  // 3. طلبات مارت: قائمة جانبية على اليمين وشاشة تفاصيل ديناميكية بالكامل على اليسار
  Widget _buildTalabatTab() {
    if (_talabatSheets.isEmpty) {
      return const Center(
        child: Text('جاري تحميل شيتات طلبات مارت...', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
      );
    }

    return _UniversalSearchList(
      items: _talabatSheets,
      titleKey: 'display_title',
      subtitleBuilder: (item) {
        final date = item['date'] ?? item['sheet_name'] ?? '';
        final isL = item['type'] == 'lamb_report';
        return isL ? 'تاريخ: $date | حسبة الخروف' : 'تاريخ: $date | كشف طلبات';
      },
      costBuilder: (item) {
        if (item['type'] == 'lamb_report') {
          return ((item['invoice_total'] ?? item['cuts_total_value'] ?? 0.0) as num).toDouble();
        }
        return ((item['total_sales'] ?? 0.0) as num).toDouble();
      },
      detailBuilder: (item) {
        final isLamb = item['type'] == 'lamb_report';
        return SingleChildScrollView(
          child: isLamb ? _buildLambReport(item) : _buildDailySheet(item),
        );
      },
    );
  }

  Widget _buildLambReport(Map<String, dynamic> data) {
    final cuts = data['cuts'] as List? ?? [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Card(
          elevation: 0,
          color: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16), side: const BorderSide(color: Color(0xFFE2E8F0))),
          child: Padding(
            padding: const EdgeInsets.all(22.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(color: MarkaziaColors.orange.withOpacity(0.12), borderRadius: BorderRadius.circular(12)),
                      child: const Icon(Icons.receipt_long_rounded, color: MarkaziaColors.orange, size: 28),
                    ),
                    const SizedBox(width: 14),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('حسبة تفصيل وتقطيع الخروف (${data['sheet_name']})',
                            style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: MarkaziaColors.dark)),
                        const Text('المطابقة الرسمية الديناميكية للفاتورة والأوزان والقطعيات', style: TextStyle(fontSize: 12, color: Colors.black54)),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 18),
                const Divider(height: 1),
                const SizedBox(height: 18),
                Row(
                  children: [
                    _kpiTile('عدد الخرفان', '${data['sheep_count']} خروف', Colors.grey.shade800),
                    const SizedBox(width: 12),
                    _kpiTile('سعر الكيلو (فاتورة)', '${((data['price_per_kg'] ?? 0.0) as num).toStringAsFixed(2)} د.أ', Colors.blueGrey.shade800),
                    const SizedBox(width: 12),
                    _kpiTile('إجمالي الفاتورة', '${((data['invoice_total'] ?? 0.0) as num).toStringAsFixed(2)} د.أ', MarkaziaColors.orange),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    _kpiTile('الوزن عند الاستلام (الفاتورة)', '${((data['weight_received'] ?? 0.0) as num).toStringAsFixed(2)} كغ', Colors.grey.shade700),
                    const SizedBox(width: 12),
                    _kpiTile('الوزن قبل التقطيع', '${((data['weight_cut'] ?? 0.0) as num).toStringAsFixed(2)} كغ', Colors.indigo.shade800),
                    const SizedBox(width: 12),
                    _kpiTile('الفاقد بالتقطيع', '${((data['waste_loss'] ?? 0.0) as num).toStringAsFixed(2)} كغ', Colors.red.shade800),
                    const SizedBox(width: 12),
                    _kpiTile('صافي الوزن بعد التقطيع', '${((data['weight_cut'] ?? 0.0) as num).toStringAsFixed(2)} كغ', Colors.green.shade800),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 20),
        const Text('جدول تفصيل القطعيات وأسعارها وإجمالياتها ونسبها الفعلية:',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: MarkaziaColors.dark)),
        const SizedBox(height: 10),
        Card(
          elevation: 0,
          color: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14), side: const BorderSide(color: Color(0xFFE2E8F0))),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(14),
            child: Table(
              columnWidths: const {
                0: FlexColumnWidth(2.8), 1: FlexColumnWidth(1.2),
                2: FlexColumnWidth(1.0), 3: FlexColumnWidth(1.2), 4: FlexColumnWidth(1.5),
              },
              children: [
                TableRow(
                  decoration: const BoxDecoration(color: Color(0xFFF3F4F6)),
                  children: const [
                    Padding(padding: EdgeInsets.all(14.0), child: Text('اسم الصنف / القطعية', style: TextStyle(fontWeight: FontWeight.bold))),
                    Padding(padding: EdgeInsets.all(14.0), child: Text('الكمية (كغ)', style: TextStyle(fontWeight: FontWeight.bold))),
                    Padding(padding: EdgeInsets.all(14.0), child: Text('النسبة %', style: TextStyle(fontWeight: FontWeight.bold))),
                    Padding(padding: EdgeInsets.all(14.0), child: Text('السعر (د.أ)', style: TextStyle(fontWeight: FontWeight.bold))),
                    Padding(padding: EdgeInsets.all(14.0), child: Text('الإجمالي (د.أ)', style: TextStyle(fontWeight: FontWeight.bold))),
                  ],
                ),
                ...cuts.map<TableRow>((c) {
                  Color rowBg = Colors.white;
                  if (c['status'] == 'highlight_yellow') rowBg = const Color(0xFFFEF9C3);
                  if (c['status'] == 'highlight_red') rowBg = const Color(0xFFFEE2E2);

                  return TableRow(
                    decoration: BoxDecoration(color: rowBg, border: const Border(top: BorderSide(color: Color(0xFFF1F5F9)))),
                    children: [
                      Padding(padding: const EdgeInsets.all(12.0), child: Text(c['name'].toString(), style: const TextStyle(fontWeight: FontWeight.w600))),
                      Padding(padding: const EdgeInsets.all(12.0), child: Text('${c['qty']} كغ')),
                      Padding(padding: const EdgeInsets.all(12.0), child: Text(c['percentage'].toString(), style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.black54))),
                      Padding(padding: const EdgeInsets.all(12.0), child: Text('${c['price']} د.أ')),
                      Padding(
                        padding: const EdgeInsets.all(12.0),
                        child: Text('${((c['total'] ?? 0.0) as num).toStringAsFixed(3)} د.أ',
                            style: const TextStyle(fontWeight: FontWeight.bold, color: MarkaziaColors.dark)),
                      ),
                    ],
                  );
                }).toList(),
                TableRow(
                  decoration: const BoxDecoration(color: Color(0xFF18181B)),
                  children: [
                    const Padding(padding: EdgeInsets.all(14.0), child: Text('المجموع الإجمالي للقطعيات الصافية', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white))),
                    Padding(padding: const EdgeInsets.all(14.0), child: Text('${data['weight_cut']} كغ', style: const TextStyle(fontWeight: FontWeight.bold, color: MarkaziaColors.orange))),
                    const Padding(padding: EdgeInsets.all(14.0), child: Text('100%', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white70))),
                    const Padding(padding: EdgeInsets.all(14.0), child: Text('—', style: TextStyle(color: Colors.white54))),
                    Padding(
                      padding: const EdgeInsets.all(14.0),
                      child: Text('${data['cuts_total_value']} د.أ',
                          style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 16, color: MarkaziaColors.orange)),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDailySheet(Map<String, dynamic> data) {
    final items = data['items'] as List? ?? [];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Card(
          elevation: 0, color: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16), side: const BorderSide(color: Color(0xFFE2E8F0))),
          child: Padding(
            padding: const EdgeInsets.all(20.0),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(data['display_title'] ?? 'كشف طلبات', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: MarkaziaColors.dark)),
                      const SizedBox(height: 4),
                      Text('إجمالي الأصناف: ${data['items_count']} صنف', style: const TextStyle(color: Colors.black54)),
                    ],
                  ),
                ),
                _kpiTile('إجمالي المبيعات', '${((data['total_sales'] ?? 0.0) as num).toStringAsFixed(3)} د.أ', MarkaziaColors.orange),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        Card(
          elevation: 0, color: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14), side: const BorderSide(color: Color(0xFFE2E8F0))),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: DataTable(
              headingRowColor: MaterialStateProperty.all(const Color(0xFFFBF9F5)),
              columns: const [
                DataColumn(label: Text('اسم الصنف', style: TextStyle(fontWeight: FontWeight.bold))),
                DataColumn(label: Text('SKU', style: TextStyle(fontWeight: FontWeight.bold))),
                DataColumn(label: Text('الكمية', style: TextStyle(fontWeight: FontWeight.bold))),
                DataColumn(label: Text('السعر', style: TextStyle(fontWeight: FontWeight.bold))),
                DataColumn(label: Text('الإجمالي', style: TextStyle(fontWeight: FontWeight.bold))),
              ],
              rows: items.map<DataRow>((it) {
                return DataRow(cells: [
                  DataCell(Text(it['name'].toString(), style: const TextStyle(fontWeight: FontWeight.w600))),
                  DataCell(Text(it['sku'].toString())),
                  DataCell(Text('${it['quantity']}')),
                  DataCell(Text('${it['price']} د.أ')),
                  DataCell(Text('${((it['total'] ?? 0.0) as num).toStringAsFixed(3)} د.أ', style: const TextStyle(fontWeight: FontWeight.bold, color: MarkaziaColors.orange))),
                ]);
              }).toList(),
            ),
          ),
        ),
      ],
    );
  }

  // 4. دليل أودو الشامل
  Widget _buildOdooCatalogTab() {
    return _UniversalSearchList(
      items: _odooCatalog,
      titleKey: 'name',
      subtitleBuilder: (item) => 'كود: ${item['code']} | فئة: ${item['category']}',
      costBuilder: (item) => (item['total_cost'] as num).toDouble(),
      detailBuilder: (item) {
        return Card(
          elevation: 0,
          color: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: const BorderSide(color: Color(0xFFE2E8F0)),
          ),
          child: Padding(
            padding: const EdgeInsets.all(22.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item['name'], style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: MarkaziaColors.dark)),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 12,
                  runSpacing: 8,
                  children: [
                    buildCopyBadge(context, label: 'كود أودو', code: item['code']),
                    if (item['barcode'].toString().isNotEmpty)
                      buildCopyBadge(context, label: 'الباركود', code: item['barcode'], color: MarkaziaColors.dark),
                    Chip(
                      label: Text('الفئة: ${item['category']}', style: const TextStyle(fontSize: 12)),
                      backgroundColor: const Color(0xFFF8FAFC),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                const Divider(height: 1),
                const SizedBox(height: 16),
                Row(
                  children: [
                    _kpiTile('الكمية', '${item['quantity']} ${item['unit']}', Colors.indigo.shade800),
                    const SizedBox(width: 16),
                    _kpiTile('كلفة الوحدة (الشراء)', '${(item['cost_per_unit'] as num).toStringAsFixed(3)} د.أ', Colors.grey.shade700),
                    const SizedBox(width: 16),
                    _kpiTile('إجمالي كلفة الكمية', '${(item['total_cost'] as num).toStringAsFixed(3)} د.أ', MarkaziaColors.orange),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _kpiTile(String title, String value, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        decoration: BoxDecoration(
          color: color.withOpacity(0.08),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: color.withOpacity(0.2)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.grey.shade600)),
            const SizedBox(height: 4),
            Text(value, style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: color)),
          ],
        ),
      ),
    );
  }
}

class _UniversalSearchList extends StatefulWidget {
  final List<dynamic> items;
  final String titleKey;
  final String Function(Map<String, dynamic>) subtitleBuilder;
  final double Function(Map<String, dynamic>)? costBuilder;
  final double Function(Map<String, dynamic>)? marginBuilder;
  final Widget Function(Map<String, dynamic>) detailBuilder;
  final bool isStaffTab;

  const _UniversalSearchList({
    required this.items,
    required this.titleKey,
    required this.subtitleBuilder,
    required this.detailBuilder,
    this.costBuilder,
    this.marginBuilder,
    this.isStaffTab = false,
  });

  @override
  State<_UniversalSearchList> createState() => _UniversalSearchListState();
}

class _UniversalSearchListState extends State<_UniversalSearchList> {
  final TextEditingController _ctrl = TextEditingController();
  List<dynamic> _filtered = [];
  Map<String, dynamic>? _selected;

  @override
  void initState() {
    super.initState();
    _filtered = widget.items;
    if (_filtered.isNotEmpty) _selected = _filtered.first;
  }

  @override
  void didUpdateWidget(covariant _UniversalSearchList oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.items != widget.items) {
      _filter(_ctrl.text);
    }
  }

  void _filter(String q) {
    final query = q.trim().toLowerCase();
    setState(() {
      _filtered = widget.items.where((i) {
        final title = (i[widget.titleKey] ?? '').toString().toLowerCase();
        final code = (i['code'] ?? i['sku'] ?? i['barcode'] ?? i['odoo_code'] ?? '').toString().toLowerCase();
        final date = (i['date'] ?? i['sheet_name'] ?? '').toString().toLowerCase();

        final ings = (i['ingredients'] as List? ?? []);
        final ingMatch = ings.any((ing) {
          final n = (ing['name'] ?? '').toString().toLowerCase();
          final c = (ing['code'] ?? '').toString().toLowerCase();
          final r = (ing['raw_description'] ?? '').toString().toLowerCase();
          return n.contains(query) || c.contains(query) || r.contains(query);
        });

        final cuts = (i['cuts'] as List? ?? []);
        final cutMatch = cuts.any((cut) {
          final n = (cut['name'] ?? '').toString().toLowerCase();
          return n.contains(query);
        });

        return query.isEmpty || title.contains(query) || code.contains(query) || date.contains(query) || ingMatch || cutMatch;
      }).toList();

      if (_filtered.isNotEmpty && !_filtered.contains(_selected)) {
        _selected = _filtered.first;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        SizedBox(
          width: 365,
          child: Container(
            color: Colors.white,
            child: Column(
              children: [
                Container(
                  margin: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFBF9F5),
                    borderRadius: BorderRadius.circular(30),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: TextField(
                    controller: _ctrl,
                    onChanged: _filter,
                    decoration: InputDecoration(
                      hintText: 'بحث بالاسم، التاريخ، الكود، أو الصنف...',
                      prefixIcon: const Icon(Icons.search_rounded, color: MarkaziaColors.orange),
                      suffixIcon: _ctrl.text.isNotEmpty
                          ? IconButton(icon: const Icon(Icons.clear, size: 16), onPressed: () { _ctrl.clear(); _filter(''); })
                          : null,
                      border: InputBorder.none,
                      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 11),
                    ),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 2),
                  child: Row(
                    children: [
                      Text('إجمالي النتائج: ${_filtered.length}',
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey.shade500)),
                    ],
                  ),
                ),
                const SizedBox(height: 6),
                const Divider(height: 1, thickness: 1, color: Color(0xFFE2E8F0)),
                Expanded(
                  child: ListView.separated(
                    itemCount: _filtered.length,
                    separatorBuilder: (_, __) => const Divider(height: 1, thickness: 1, color: Color(0xFFF8FAFC)),
                    itemBuilder: (context, idx) {
                      final item = _filtered[idx] as Map<String, dynamic>;
                      final isSel = item == _selected;
                      final cost = widget.costBuilder != null ? widget.costBuilder!(item) : null;
                      final margin = widget.marginBuilder != null ? widget.marginBuilder!(item) : null;

                      return ListTile(
                        dense: true,
                        selected: isSel,
                        selectedTileColor: MarkaziaColors.orange.withOpacity(0.09),
                        shape: isSel ? const Border(right: BorderSide(color: MarkaziaColors.orange, width: 4)) : null,
                        title: Text(item[widget.titleKey] ?? '',
                            style: TextStyle(
                              fontWeight: isSel ? FontWeight.bold : FontWeight.w600,
                              color: isSel ? MarkaziaColors.orange : MarkaziaColors.dark,
                            )),
                        subtitle: Row(
                          children: [
                            Icon(
                              item['type'] == 'lamb_report' ? Icons.receipt_long_rounded : (widget.isStaffTab ? Icons.calendar_today_rounded : Icons.info_outline),
                              size: 12,
                              color: isSel ? MarkaziaColors.orange : Colors.grey.shade500,
                            ),
                            const SizedBox(width: 4),
                            Expanded(
                              child: Text(
                                widget.subtitleBuilder(item),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: TextStyle(fontSize: 11, color: isSel ? MarkaziaColors.orange : Colors.grey.shade600),
                              ),
                            ),
                          ],
                        ),
                        trailing: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            if (cost != null)
                              Text('${cost.toStringAsFixed(2)} د.أ',
                                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: MarkaziaColors.dark)),
                            if (margin != null && margin != 0.0)
                              Text('${(margin * 100).toStringAsFixed(0)}%',
                                  style: TextStyle(
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                      color: margin >= 0.2 ? Colors.green.shade700 : MarkaziaColors.orange)),
                          ],
                        ),
                        onTap: () => setState(() => _selected = item),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        ),
        const VerticalDivider(width: 1, thickness: 1, color: Color(0xFFE2E8F0)),
        Expanded(
          child: _selected == null
              ? const Center(child: Text('اختر عنصراً لعرض تفاصيله الكاملة'))
              : Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: widget.detailBuilder(_selected!),
                ),
        ),
      ],
    );
  }
}
