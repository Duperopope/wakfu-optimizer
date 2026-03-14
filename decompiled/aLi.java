/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
import java.util.HashMap;

public class aLi
implements aqz {
    protected int o;
    protected aLj[] ehA;
    protected aLj[] ehB;
    protected aLk ehC;
    protected aLk ehD;
    protected HashMap<Short, Byte> ehE;
    protected HashMap<Short, Byte> ehF;

    public int d() {
        return this.o;
    }

    public aLj[] ckQ() {
        return this.ehA;
    }

    public aLj[] ckR() {
        return this.ehB;
    }

    public aLk ckS() {
        return this.ehC;
    }

    public aLk ckT() {
        return this.ehD;
    }

    public HashMap<Short, Byte> ckU() {
        return this.ehE;
    }

    public HashMap<Short, Byte> ckV() {
        return this.ehF;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.ehA = null;
        this.ehB = null;
        this.ehC = null;
        this.ehD = null;
        this.ehE = null;
        this.ehF = null;
    }

    @Override
    public void a(aqH aqH2) {
        int n;
        int n2;
        int n3;
        this.o = aqH2.bGI();
        int n4 = aqH2.bGI();
        this.ehA = new aLj[n4];
        for (n3 = 0; n3 < n4; ++n3) {
            this.ehA[n3] = new aLj();
            this.ehA[n3].a(aqH2);
        }
        n3 = aqH2.bGI();
        this.ehB = new aLj[n3];
        for (n2 = 0; n2 < n3; ++n2) {
            this.ehB[n2] = new aLj();
            this.ehB[n2].a(aqH2);
        }
        this.ehC = new aLk();
        ((aLK)this.ehC).a(aqH2);
        this.ehD = new aLk();
        ((aLK)this.ehD).a(aqH2);
        n2 = aqH2.bGI();
        this.ehE = new HashMap(n2);
        for (n = 0; n < n2; ++n) {
            short s = aqH2.bGG();
            byte by = aqH2.aTf();
            this.ehE.put(s, by);
        }
        n = aqH2.bGI();
        this.ehF = new HashMap(n);
        for (int i = 0; i < n; ++i) {
            short s = aqH2.bGG();
            byte by = aqH2.aTf();
            this.ehF.put(s, by);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oAA.d();
    }
}
