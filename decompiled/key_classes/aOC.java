/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  aqH
 *  aqz
 *  eNi
 *  ewj
 */
public class aOC
implements aqz {
    protected int bfE;
    protected int bfF;
    protected int egx;
    protected short eta;
    protected int[] etb;
    protected short etc;
    protected short etd;
    protected int[] ete;
    protected short etf;
    protected int[] etg;
    protected int[] eth;
    protected int[] eti;
    protected int[] etj;
    protected int[] etk;
    protected int[] etl;
    protected int[] etm;
    protected String etn;
    protected long[] eto;
    protected boolean bfY;
    protected int etp;
    protected float etq;
    protected boolean esK;
    protected boolean etr;
    protected short ets;
    protected float ett;
    protected float[] biv;
    protected float etu;
    protected float etv;
    protected byte etw;
    protected byte etx;
    protected byte ety;
    protected int bfW;
    protected boolean etz;
    protected short etA;
    protected float etB;
    protected byte etC;
    protected boolean etD;
    protected String etE;
    protected short etF;
    protected short etG;
    protected String etH;
    protected String etI;
    protected String etJ;
    protected boolean bfK;
    protected boolean etK;
    protected boolean etL;
    protected boolean etM;
    protected boolean etN;
    protected boolean etO;
    protected int dKh;
    protected boolean bfZ;
    protected int[] etP;
    protected boolean etQ;
    protected boolean etR;
    protected boolean etS;
    protected boolean etT;
    protected boolean etU;

    public boolean aZz() {
        return false;
    }

    public boolean cwG() {
        return false;
    }

    public boolean cwH() {
        return false;
    }

    public boolean cwI() {
        String string = this.cxu().trim();
        boolean bl = this.cxo();
        boolean bl2 = this.cwJ();
        if (bl2) {
            return false;
        }
        if (string.startsWith("ITEM")) {
            return bl && this.cwK();
        }
        String string2 = this.cxt().trim();
        return string2.startsWith("SPELL") && bl || string2.startsWith("GROUP") || string2.startsWith("BOMB") || string2.startsWith("AREA") || string2.startsWith("IEP_DESTRUCTIBLE") || string2.startsWith("STATE") && bl || string2.startsWith("TIMELINE") && bl;
    }

    public boolean cwJ() {
        if (this.etP == null) {
            return false;
        }
        for (int i = 0; i < this.etP.length; ++i) {
            int n = this.etP[i];
            eNi eNi2 = eNi.RQ((int)n);
            if (eNi2 != eNi.qWH) continue;
            return true;
        }
        return false;
    }

    public boolean cwK() {
        String string = this.cxu().trim();
        boolean bl = this.cwJ();
        if (bl) {
            return false;
        }
        if (string.startsWith("ITEM")) {
            return string.endsWith("_USE");
        }
        boolean bl2 = this.cxo();
        String string2 = this.cxt().trim();
        return !string2.startsWith("SET") && (!string2.startsWith("SPELL") || bl2) && !string2.startsWith("PROTECTOR") && !string2.startsWith("BUILDING") && !string2.startsWith("ABILITY") && !string2.startsWith("APTITUDE");
    }

    public int aZH() {
        return this.bfE;
    }

    public int avZ() {
        return this.bfF;
    }

    public int cjJ() {
        return this.egx;
    }

    public short cwL() {
        return this.eta;
    }

    public int[] cwM() {
        return this.etb;
    }

    public short cwN() {
        return this.etc;
    }

    public short cwO() {
        return this.etd;
    }

    public int[] cwP() {
        return this.ete;
    }

    public short cwQ() {
        return this.etf;
    }

    public int[] cwR() {
        return this.etg;
    }

    public int[] cwS() {
        return this.eth;
    }

    public int[] cwT() {
        return this.eti;
    }

    public int[] cwU() {
        return this.etj;
    }

    public int[] cwV() {
        return this.etk;
    }

    public int[] cwW() {
        return this.etl;
    }

    public int[] cwX() {
        return this.etm;
    }

    public String cwY() {
        return this.etn;
    }

    public long[] cwZ() {
        return this.eto;
    }

    public boolean aZT() {
        return this.bfY;
    }

    public int cxa() {
        return this.etp;
    }

    public float cxb() {
        return this.etq;
    }

    public boolean cwq() {
        return this.esK;
    }

    public boolean cxc() {
        return this.etr;
    }

    public short cxd() {
        return this.ets;
    }

    public float cxe() {
        return this.ett;
    }

    public float[] ckl() {
        return this.biv;
    }

    public float cxf() {
        return this.etu;
    }

    public float cxg() {
        return this.etv;
    }

    public byte cxh() {
        return this.etw;
    }

    public byte cxi() {
        return this.etx;
    }

    public byte cxj() {
        return this.ety;
    }

    public int aZP() {
        return this.bfW;
    }

    public boolean cxk() {
        return this.etz;
    }

    public short cxl() {
        return this.etA;
    }

    public float cxm() {
        return this.etB;
    }

    public byte cxn() {
        return this.etC;
    }

    public boolean cxo() {
        return this.etD;
    }

    public String cxp() {
        return this.etE;
    }

    public short cxq() {
        return this.etF;
    }

    public short cxr() {
        return this.etG;
    }

    public String cxs() {
        return this.etH;
    }

    public String cxt() {
        return this.etI;
    }

    public String cxu() {
        return this.etJ;
    }

    public boolean cxv() {
        return this.bfK;
    }

    public boolean cxw() {
        return this.etK;
    }

    public boolean cwA() {
        return this.etL;
    }

    public boolean cxx() {
        return this.etM;
    }

    public boolean cxy() {
        return this.etN;
    }

    public boolean cxz() {
        return this.etO;
    }

    public int cbj() {
        return this.dKh;
    }

    public boolean aZW() {
        return this.bfZ;
    }

    public int[] cxA() {
        return this.etP;
    }

    public boolean cxB() {
        return this.etQ;
    }

    public boolean cxC() {
        return this.etR;
    }

    public boolean cxD() {
        return this.etS;
    }

    public boolean cwr() {
        return this.etT;
    }

    public boolean cxE() {
        return this.etU;
    }

    public void reset() {
        this.bfE = 0;
        this.bfF = 0;
        this.egx = 0;
        this.eta = 0;
        this.etb = null;
        this.etc = 0;
        this.etd = 0;
        this.ete = null;
        this.etf = 0;
        this.etg = null;
        this.eth = null;
        this.eti = null;
        this.etj = null;
        this.etk = null;
        this.etl = null;
        this.etm = null;
        this.etn = null;
        this.eto = null;
        this.bfY = false;
        this.etp = 0;
        this.etq = 0.0f;
        this.esK = false;
        this.etr = false;
        this.ets = 0;
        this.ett = 0.0f;
        this.biv = null;
        this.etu = 0.0f;
        this.etv = 0.0f;
        this.etw = 0;
        this.etx = 0;
        this.ety = 0;
        this.bfW = 0;
        this.etz = false;
        this.etA = 0;
        this.etB = 0.0f;
        this.etC = 0;
        this.etD = false;
        this.etE = null;
        this.etF = 0;
        this.etG = 0;
        this.etH = null;
        this.etI = null;
        this.etJ = null;
        this.bfK = false;
        this.etK = false;
        this.etL = false;
        this.etM = false;
        this.etN = false;
        this.etO = false;
        this.dKh = 0;
        this.bfZ = false;
        this.etP = null;
        this.etQ = false;
        this.etR = false;
        this.etS = false;
        this.etT = false;
        this.etU = false;
    }

    public void a(aqH aqH2) {
        this.bfE = aqH2.bGI();
        this.bfF = aqH2.bGI();
        this.egx = aqH2.bGI();
        this.eta = aqH2.bGG();
        this.etb = aqH2.bGM();
        this.etc = aqH2.bGG();
        this.etd = aqH2.bGG();
        this.ete = aqH2.bGM();
        this.etf = aqH2.bGG();
        this.etg = aqH2.bGM();
        this.eth = aqH2.bGM();
        this.eti = aqH2.bGM();
        this.etj = aqH2.bGM();
        this.etk = aqH2.bGM();
        this.etl = aqH2.bGM();
        this.etm = aqH2.bGM();
        this.etn = aqH2.bGL().intern();
        this.eto = aqH2.bxz();
        this.bfY = aqH2.bxv();
        this.etp = aqH2.bGI();
        this.etq = aqH2.bGH();
        this.esK = aqH2.bxv();
        this.etr = aqH2.bxv();
        this.ets = aqH2.bGG();
        this.ett = aqH2.bGH();
        this.biv = aqH2.bxA();
        this.etu = aqH2.bGH();
        this.etv = aqH2.bGH();
        this.etw = aqH2.aTf();
        this.etx = aqH2.aTf();
        this.ety = aqH2.aTf();
        this.bfW = aqH2.bGI();
        this.etz = aqH2.bxv();
        this.etA = aqH2.bGG();
        this.etB = aqH2.bGH();
        this.etC = aqH2.aTf();
        this.etD = aqH2.bxv();
        this.etE = aqH2.bGL().intern();
        this.etF = aqH2.bGG();
        this.etG = aqH2.bGG();
        this.etH = aqH2.bGL().intern();
        this.etI = aqH2.bGL().intern();
        this.etJ = aqH2.bGL().intern();
        this.bfK = aqH2.bxv();
        this.etK = aqH2.bxv();
        this.etL = aqH2.bxv();
        this.etM = aqH2.bxv();
        this.etN = aqH2.bxv();
        this.etO = aqH2.bxv();
        this.dKh = aqH2.bGI();
        this.bfZ = aqH2.bxv();
        this.etP = aqH2.bGM();
        this.etQ = aqH2.bxv();
        this.etR = aqH2.bxv();
        this.etS = aqH2.bxv();
        this.etT = aqH2.bxv();
        this.etU = aqH2.bxv();
    }

    public final int bGA() {
        return ewj.ozF.d();
    }
}
